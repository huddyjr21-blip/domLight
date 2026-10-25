#!/usr/bin/bash
set -euo pipefail
. /etc/os-release
[[ "$ID" == fedora && "$VERSION_ID" == 44 ]] || { echo 'This repository targets Fedora 44.' >&2; exit 1; }
case "$(uname -m)" in x86_64|aarch64) ;; *) echo 'Unsupported architecture' >&2; exit 1;; esac
repo_url=https://huddyjr21-blip.github.io/domLight
workdir=$(mktemp -d)
trap 'rm -rf -- "$workdir"' EXIT
curl --fail --location --silent --show-error "$repo_url/RPM-GPG-KEY-cloud-flex" -o "$workdir/key"
printf '%s  %s\n' '5100490d0d82f480f3ba6535635268fc265d1600e5d98827f5ea0dd1cd434e96' "$workdir/key" | sha256sum --check -
curl --fail --location --silent --show-error "$repo_url/fedora/44/noarch/Packages/cloud-flex-release-0.1.0-1.fc44.noarch.rpm" -o "$workdir/release.rpm"
sudo rpmkeys --import "$workdir/key"
rpmkeys --checksig "$workdir/release.rpm"
sudo dnf --setopt=localpkg_gpgcheck=true install "$workdir/release.rpm"
sudo systemctl daemon-reload
sudo systemctl enable --now cloud-flex-update.timer
sudo dnf --refresh --assumeyes upgrade cloud-flex-desktop cloud-flex-release
printf '\nCloud Flex update enrollment is complete. Sign out after desktop updates to load all changes.\n'
