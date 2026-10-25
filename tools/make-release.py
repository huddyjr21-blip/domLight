#!/usr/bin/python3
"""Build the repository enrollment RPM after choosing the public base URL."""
import argparse,hashlib,subprocess,tarfile,urllib.parse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--base-url',required=True);p.add_argument('--key-file',type=Path,required=True);p.add_argument('--client-dir',type=Path,required=True);p.add_argument('--build-dir',type=Path,required=True);a=p.parse_args()
u=urllib.parse.urlparse(a.base_url)
if u.scheme not in ['https','http'] or not u.hostname or u.username or u.password or u.query or u.fragment:raise SystemExit('Use a plain HTTP(S) repository URL without credentials')
base=a.base_url.rstrip('/');top=a.build_dir.resolve();src=top/'cloud-flex-release-0.1.0';root=src/'root'
for d in ['SOURCES','SPECS','BUILD','BUILDROOT','RPMS','SRPMS']:(top/d).mkdir(parents=True,exist_ok=True)
key=root/'etc/pki/rpm-gpg/RPM-GPG-KEY-cloud-flex';key.parent.mkdir(parents=True,exist_ok=True);key.write_bytes(a.key_file.read_bytes())
repo=root/'etc/yum.repos.d/cloud-flex.repo';repo.parent.mkdir(parents=True,exist_ok=True)
repo.write_text('[cloud-flex]\nname=Cloud Flex tester updates\nbaseurl='+base+'/fedora/$releasever/noarch/\nenabled=1\npkg_gpgcheck=1\nrepo_gpgcheck=1\ngpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-cloud-flex\nsslverify=1\nmetadata_expire=1h\nskip_if_unavailable=False\nincludepkgs=cloud-flex-desktop cloud-flex-release\n')
units=root/'usr/lib/systemd/system';units.mkdir(parents=True,exist_ok=True)
for name in ['cloud-flex-update.service','cloud-flex-update.timer']:(units/name).write_bytes((a.client_dir/name).read_bytes())
spec='''Name: cloud-flex-release
Version: 0.1.0
Release: 1%{?dist}
Summary: Signed update repository configuration for Cloud Flex testers
License: MIT
BuildArch: noarch
Source0: cloud-flex-release-0.1.0.tar.gz
Requires: dnf5
Requires: systemd
%description
Repository public key, signed repository configuration and opt-in update timer.
%prep
%setup -q
%build
%install
mkdir -p %{buildroot}
cp -a root/. %{buildroot}/
%files
%config(noreplace) /etc/yum.repos.d/cloud-flex.repo
/etc/pki/rpm-gpg/RPM-GPG-KEY-cloud-flex
/usr/lib/systemd/system/cloud-flex-update.service
/usr/lib/systemd/system/cloud-flex-update.timer
'''
(top/'SPECS/cloud-flex-release.spec').write_text(spec)
with tarfile.open(top/'SOURCES/cloud-flex-release-0.1.0.tar.gz','w:gz') as t:t.add(src,arcname=src.name)
subprocess.run(['rpmbuild','-ba','--define','_topdir '+str(top),str(top/'SPECS/cloud-flex-release.spec')],check=True)
