#!/usr/bin/env python3
"""Regression tests for OpenClaw installer plugin allowlist handling (#7208).

Validates that malformed plugins and plugins.allow configurations are rejected
before mutation, preventing crashes and allowlist corruption.
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

# Add scripts directory to path to import install_openclaw
SCRIPT_DIR = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "os-skills"
    / "ai"
    / "install-openclaw"
    / "scripts"
)
sys.path.insert(0, str(SCRIPT_DIR))

import install_openclaw  # noqa: E402


class TestMergePluginAllow(unittest.TestCase):
    def test_merge_plugin_allow_normal(self):
        existing = {"plugins": {"allow": ["plugin_a", "plugin_b"]}}
        merged = {"plugins": {"allow": ["plugin_b", "plugin_c"]}}
        result = install_openclaw.merge_plugin_allow(existing, merged)
        self.assertEqual(
            result["plugins"]["allow"],
            ["plugin_a", "plugin_b", "plugin_c"],
        )

    def test_merge_plugin_allow_handles_none_plugins(self):
        existing = {"plugins": None}
        merged = {"plugins": {"allow": ["dingtalk"]}}
        result = install_openclaw.merge_plugin_allow(existing, merged)
        self.assertEqual(result["plugins"]["allow"], ["dingtalk"])

    def test_merge_plugin_allow_handles_non_list_allow(self):
        existing = {"plugins": {"allow": "dingtalk"}}
        merged = {"plugins": {"allow": ["dingtalk"]}}
        result = install_openclaw.merge_plugin_allow(existing, merged)
        self.assertEqual(result["plugins"]["allow"], ["dingtalk"])

    def test_merge_plugin_allow_no_merged_allow(self):
        existing = {"plugins": {"allow": ["existing_plugin"]}}
        merged = {"models": {"default": "qwen"}}
        result = install_openclaw.merge_plugin_allow(existing, merged)
        self.assertNotIn("plugins", result)


class TestApplyConfigValidation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.tmp.name) / "openclaw.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_rejects_null_plugins_before_write(self):
        content = json.dumps({"plugins": None, "models": {}})
        self.config_path.write_text(content, encoding="utf-8")
        backup_path = self.config_path.with_name(self.config_path.name + ".bak")

        with self.assertRaises(SystemExit) as ctx:
            install_openclaw.apply_config({"models": {"foo": "bar"}}, self.config_path)

        self.assertIn("'plugins' must be a JSON object", str(ctx.exception))
        # Verify file was not mutated and backup was not created
        self.assertEqual(self.config_path.read_text(encoding="utf-8"), content)
        self.assertFalse(backup_path.exists())

    def test_rejects_string_plugins_before_write(self):
        content = json.dumps({"plugins": "invalid_string"})
        self.config_path.write_text(content, encoding="utf-8")
        backup_path = self.config_path.with_name(self.config_path.name + ".bak")

        with self.assertRaises(SystemExit) as ctx:
            install_openclaw.apply_config({"models": {}}, self.config_path)

        self.assertIn("'plugins' must be a JSON object", str(ctx.exception))
        self.assertEqual(self.config_path.read_text(encoding="utf-8"), content)
        self.assertFalse(backup_path.exists())

    def test_rejects_string_plugins_allow_before_write(self):
        content = json.dumps({"plugins": {"allow": "dingtalk"}})
        self.config_path.write_text(content, encoding="utf-8")
        backup_path = self.config_path.with_name(self.config_path.name + ".bak")

        with self.assertRaises(SystemExit) as ctx:
            install_openclaw.apply_config(
                {"plugins": {"allow": ["dingtalk"]}}, self.config_path
            )

        self.assertIn("'plugins.allow' must be a list", str(ctx.exception))
        self.assertEqual(self.config_path.read_text(encoding="utf-8"), content)
        self.assertFalse(backup_path.exists())

    def test_rejects_null_plugins_allow_before_write(self):
        content = json.dumps({"plugins": {"allow": None}})
        self.config_path.write_text(content, encoding="utf-8")
        backup_path = self.config_path.with_name(self.config_path.name + ".bak")

        with self.assertRaises(SystemExit) as ctx:
            install_openclaw.apply_config(
                {"plugins": {"allow": ["dingtalk"]}}, self.config_path
            )

        self.assertIn("'plugins.allow' must be a list", str(ctx.exception))
        self.assertEqual(self.config_path.read_text(encoding="utf-8"), content)
        self.assertFalse(backup_path.exists())

    def test_accepts_valid_allowlist_and_merges(self):
        content = json.dumps({"plugins": {"allow": ["custom_plugin"]}})
        self.config_path.write_text(content, encoding="utf-8")

        install_openclaw.apply_config(
            {"plugins": {"allow": ["dingtalk"]}}, self.config_path
        )

        saved = json.loads(self.config_path.read_text(encoding="utf-8"))
        self.assertEqual(
            saved["plugins"]["allow"],
            ["custom_plugin", "dingtalk"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
