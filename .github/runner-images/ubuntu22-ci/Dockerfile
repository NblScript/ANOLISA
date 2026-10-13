FROM anolisa-runner-registry-vpc.ap-southeast-1.cr.aliyuncs.com/anolisa/anolisa@sha256:d6085d6fef416c18d2f75034578dd9e7fa8d8a47d439c2257263f3a4b46216cb
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake pkg-config libsystemd-dev libssl-dev elfutils zlib1g-dev \
    btrfs-progs fuse3 libfuse3-dev ripgrep zsh shellcheck perl \
    && rm -rf /var/lib/apt/lists/*
COPY install-tools.sh verify-tools.sh /opt/anolisa/
RUN bash /opt/anolisa/install-tools.sh \
    && chown -R runner:runner /opt/hostedtoolcache /opt/anolisa/ci-tools /home/runner
ENV PATH="/opt/anolisa/ci-tools/bin:/opt/hostedtoolcache/node/20.20.2/x64/bin:/home/runner/.cargo/bin:${PATH}" \
    RUSTUP_DIST_SERVER=https://static.rust-lang.org \
    RUSTUP_UPDATE_ROOT=https://static.rust-lang.org/rustup
USER runner
RUN bash /opt/anolisa/verify-tools.sh
