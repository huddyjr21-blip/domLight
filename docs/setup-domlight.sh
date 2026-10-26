#!/usr/bin/bash
# Run as your normal user from the installed Fedora KDE desktop.
set -euo pipefail
[[ $EUID -ne 0 ]] || { echo 'Run without sudo; administrator access is requested for package installation.' >&2; exit 1; }
. /etc/os-release
[[ $ID == fedora && $VERSION_ID == 44 ]] || { echo 'Requires Fedora 44.' >&2; exit 1; }
case $(uname -m) in x86_64|aarch64) ;; *) echo 'Unsupported architecture.' >&2; exit 1;; esac
[[ ${XDG_CURRENT_DESKTOP:-} == *KDE* ]] || { echo 'Run from your installed Plasma desktop.' >&2; exit 1; }
[[ ! -d /run/initramfs/live ]] || { echo 'Install Fedora and reboot into the internal drive first.' >&2; exit 1; }
repo_url=https://huddyjr21-blip.github.io/domLight
workdir=$(mktemp -d)
trap 'rm -rf -- "$workdir"' EXIT
curl --fail --location --silent --show-error "$repo_url/RPM-GPG-KEY-cloud-flex" -o "$workdir/key"
printf '%s  %s\n' 5100490d0d82f480f3ba6535635268fc265d1600e5d98827f5ea0dd1cd434e96 "$workdir/key" | sha256sum --check -
curl --fail --location --silent --show-error "$repo_url/fedora/44/noarch/Packages/cloud-flex-release-0.1.0-1.fc44.noarch.rpm" -o "$workdir/release.rpm"
curl --fail --location --silent --show-error "$repo_url/fedora/44/noarch/Packages/cloud-flex-desktop-0.1.2-1.fc44.noarch.rpm" -o "$workdir/desktop.rpm"
printf '%s  %s\n' 4633a9b4f80cfb48cb07a6aa652749bfe0a939418bd07a5e8a44debc2c3cdc50 "$workdir/release.rpm" 494544e54e4209d13495fc00f05648269c344021257bc4ed96022e6905bf7d33 "$workdir/desktop.rpm" | sha256sum --check -
echo 'Installs domLight, replaces Dolphin with Nemo, and enables daily signed desktop updates.'
sudo rpmkeys --import "$workdir/key"
rpmkeys --checksig "$workdir/release.rpm" "$workdir/desktop.rpm"
sudo dnf --refresh --setopt=localpkg_gpgcheck=true install systemd-pam "$workdir/release.rpm" "$workdir/desktop.rpm"
python3 /usr/share/cloud-flex/setup.py --apply
sudo systemctl daemon-reload
sudo systemctl enable --now cloud-flex-update.timer
printf '\nInstalled domLight. Sign out and back in to load the complete desktop.\n'
