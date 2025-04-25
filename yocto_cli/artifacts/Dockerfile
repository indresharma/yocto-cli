FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends\
    gawk wget git-core diffstat unzip \
    texinfo gcc-multilib build-essential chrpath socat cpio \
    python3 python3-pip python3-pexpect xz-utils debianutils \
    python3-git python3-gi python3-jinja2 libegl1-mesa libsdl1.2-dev xterm locales \
    vim bash-completion screen jq gcc-multilib git-lfs file liblz4-tool zstd graphviz \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

RUN useradd -m -s /bin/bash yocto

USER yocto

WORKDIR /home/yocto/
