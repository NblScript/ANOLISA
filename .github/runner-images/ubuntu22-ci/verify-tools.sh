#!/usr/bin/env bash
set -euo pipefail
for version in 1.86.0 1.88.0 1.89.0 1.91.0 1.93.0 1.93.1 1.97.1 1.98.0; do
    rustup run "$version" rustc --version
    rustup run "$version" cargo fmt --version
    rustup run "$version" cargo clippy --version
done
for version in 1.89.0 1.93.0 1.93.1; do
    sysroot=$(rustup run "$version" rustc --print sysroot)
    "$sysroot/lib/rustlib/x86_64-unknown-linux-gnu/bin/llvm-profdata" --version
done
for version in 20.20.2 22.23.2; do
    test -f "/opt/hostedtoolcache/node/$version/x64.complete"
    test "$(/opt/hostedtoolcache/node/"$version"/x64/bin/node --version)" = "v$version"
    /opt/hostedtoolcache/node/"$version"/x64/bin/npm --version
done
test -f /opt/hostedtoolcache/Python/3.11.17/x64.complete
/opt/hostedtoolcache/Python/3.11.17/x64/bin/python3 --version
uv python find 3.11.6
for version in 0.11.7 0.13.0; do
    test -f "/opt/hostedtoolcache/uv/$version/x86_64.complete"
    /opt/hostedtoolcache/uv/"$version"/x86_64/uv --version
done
[[ "$(cargo tarpaulin --version)" == *' 0.37.2' ]]
test "$(cargo sbom --version)" = 'cargo-sbom 0.10.0'
test "$(cargo llvm-cov --version)" = 'cargo-llvm-cov 0.9.1'
test "$(just --version)" = 'just 1.58.0'
diff-cover --version
sccache --version
cmake --version
pkg-config --exists libsystemd openssl
shellcheck --version
rg --version
zsh --version
