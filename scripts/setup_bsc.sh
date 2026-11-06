#!/usr/bin/env bash
set -euo pipefail

BSC_VERSION="2026.07.1"
INSTALL_DIR="${HOME}/.local/bsc"

if [ -x "${INSTALL_DIR}/bin/bsc" ]; then
    echo "Bluespec compiler (bsc) already installed at ${INSTALL_DIR}/bin/bsc:"
    "${INSTALL_DIR}/bin/bsc" -v
    exit 0
fi

echo "Installing Bluespec Compiler (bsc ${BSC_VERSION}) into ${INSTALL_DIR}..."
mkdir -p "${INSTALL_DIR}"

OS="$(uname -s)"
ARCH="$(uname -m)"
TARBALL="bsc-${BSC_VERSION}-debian-12.15.tar.gz"

if [ "${OS}" = "Darwin" ]; then
    if [ "${ARCH}" = "arm64" ]; then
        TARBALL="bsc-${BSC_VERSION}-macos-15.tar.gz"
    else
        TARBALL="bsc-${BSC_VERSION}-macos-15-intel.tar.gz"
    fi
elif [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "${ID:-}" = "ubuntu" ]; then
        if [ "${ARCH}" = "aarch64" ]; then
            TARBALL="bsc-${BSC_VERSION}-ubuntu-24.04-arm.tar.gz"
        else
            TARBALL="bsc-${BSC_VERSION}-ubuntu-24.04.tar.gz"
        fi
    fi
fi

URL="https://github.com/B-Lang-org/bsc/releases/download/${BSC_VERSION}/${TARBALL}"
echo "Downloading ${URL}..."
curl -L -s "${URL}" | tar -xzmf - --strip-components=1 -C "${INSTALL_DIR}"

echo "Verifying bsc installation..."
"${INSTALL_DIR}/bin/bsc" -v
echo "Done! Add ${INSTALL_DIR}/bin to your PATH and set BLUESPECDIR=${INSTALL_DIR}/lib."
