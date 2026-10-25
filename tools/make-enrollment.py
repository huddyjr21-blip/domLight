#!/usr/bin/python3
import argparse,hashlib,urllib.parse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--key-file',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
u=urllib.parse.urlparse(a.base_url)
if u.scheme not in ['https','http'] or not u.hostname or u.username or u.password or u.query or u.fragment:raise SystemExit('Invalid repository URL')
url=a.base_url.rstrip('/');keyhash=hashlib.sha256(a.key_file.read_bytes()).hexdigest()
script='''#!/usr/bin/bash
set -euo pipefail
. /etc/os-release
[[ "$ID" == fedora && "$VERSION_ID" == 44 ]] || { echo 'This repository targets Fedora 44.' >&2; exit 1; }
case "$(uname -m)" in x86_64|aarch64) ;; *) echo 'Unsupported architecture' >&2; exit 1;; esac
repo_url=@URL@
workdir=$(mktemp -d)
trap 'rm -rf -- "$workdir"' EXIT
curl --fail --location --silent --show-error "$repo_url/RPM-GPG-KEY-cloud-flex" -o "$workdir/key"
printf '%s  %s\\n' '@HASH@' "$workdir/key" | sha256sum --check -
curl --fail --location --silent --show-error "$repo_url/fedora/44/noarch/Packages/cloud-flex-release-0.1.0-1.fc44.noarch.rpm" -o "$workdir/release.rpm"
sudo rpmkeys --import "$workdir/key"
rpmkeys --checksig "$workdir/release.rpm"
sudo dnf --setopt=localpkg_gpgcheck=true install "$workdir/release.rpm"
sudo systemctl daemon-reload
sudo systemctl enable --now cloud-flex-update.timer
sudo dnf --refresh --assumeyes upgrade cloud-flex-desktop cloud-flex-release
printf '\\nCloud Flex update enrollment is complete. Sign out after desktop updates to load all changes.\\n'
'''
import shlex
script=script.replace('@URL@',shlex.quote(url)).replace('@HASH@',keyhash)
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(script);a.output.chmod(0o755)
print('Enrollment script generated:',a.output)
