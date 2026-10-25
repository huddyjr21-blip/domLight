"""Resolve the full x86-64 installation transaction without installing it on the ARM build VM."""
from pathlib import Path
import subprocess, urllib.request, json, os

work = Path.home()/'.cache/domlight-offline-0.1.3'
work.mkdir(parents=True, exist_ok=True)
public = Path('/tmp/domlight-0.1.3-export')
public.mkdir(exist_ok=True)
base = 'http://192.168.64.1:8765/'
ks = work/'domLight-0.1.3-x86_64.ks'
urllib.request.urlretrieve(base+'cloud-flex-port/'+ks.name, ks)
packages = work/'repo/Packages'
packages.mkdir(parents=True, exist_ok=True)
custom = []
for name in ['cloud-flex-desktop-0.1.1-1.fc44.noarch.rpm', 'cloud-flex-release-0.1.0-1.fc44.noarch.rpm']:
    target = packages/name
    urllib.request.urlretrieve(base+'domLight/docs/fedora/44/noarch/Packages/'+name, target)
    custom.append(str(target))
lines = ks.read_text().split('%packages --exclude-weakdeps\n',1)[1].split('%end',1)[0].splitlines()
roots = [x for x in lines if x and not x.startswith(('#','-')) and x not in ['cloud-flex-desktop','cloud-flex-release']]
exclude = [x[1:] for x in lines if x.startswith('-')]
cmd = ['sudo','dnf','--releasever=44','--forcearch=x86_64',
       '--installroot='+str(work/'resolve-root'), '--use-host-config',
       '--disable-repo=*',
       '--repofrompath=domlight-base,https://dl.fedoraproject.org/pub/fedora/linux/releases/44/Everything/x86_64/os/',
       '--repofrompath=domlight-updates,https://dl.fedoraproject.org/pub/fedora/linux/updates/44/Everything/x86_64/',
       '--setopt=cachedir='+str(work/'cache'), '--setopt=keepcache=True', '--setopt=install_weak_deps=False','--setopt=multilib_policy=best',
       '--exclude='+','.join(exclude),'install','-y','--downloadonly',
       *roots, *custom]
print('Preparing offline transaction:', ' '.join(cmd),flush=True)
subprocess.run(cmd,check=True)
# Download-only install keeps RPMs in its isolated DNF cache.
import shutil
for cache in [work/'cache', work/'resolve-root'/str(work/'cache').lstrip('/')]:
    if cache.exists():
        for f in cache.rglob('*.rpm'):
            if not (packages/f.name).exists():shutil.copy2(f,packages/f.name)
files = list(packages.glob('*.rpm'))
assert len(files)>100, 'Incomplete installation package set'
manifest=[]
for f in files:
    fields=subprocess.check_output(['rpm','-qp','--qf','%{NAME}|%{VERSION}-%{RELEASE}|%{ARCH}',str(f)],text=True).split('|')
    assert fields[2] in ['x86_64','noarch'],fields
    manifest.append(dict(zip(['name','version','arch'],fields),file=f.name,bytes=f.stat().st_size))
(public/'package-manifest.json').write_text(json.dumps(sorted(manifest,key=lambda p:p['name']),indent=2))
print('OFFLINE_PACKAGES_READY',len(files),sum(f.stat().st_size for f in files),flush=True)
