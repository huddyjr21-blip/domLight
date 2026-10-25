"""Build a self-contained domLight USB installer from signed Fedora media and RPMs."""
from pathlib import Path
import urllib.request, subprocess, hashlib, shutil, re, json, configparser, xml.etree.ElementTree as ET

home=Path.home()
b=home/'.cache/domlight-offline-0.1.3'
public=Path('/tmp/domlight-0.1.3-export');public.mkdir(exist_ok=True)
repo=b/'repo'
base=Path('/tmp/cloud-flex-iso/fedora-base.iso')
assert hashlib.file_digest(base.open('rb'),'sha256').hexdigest()=='bd285201494dd0ba09b54d05ac707de1401668b8512a573edb5922dcf9d7067e'
log=[]
def run(args,timeout=600):
    p=subprocess.run(list(map(str,args)),text=True,capture_output=True,stdin=subprocess.DEVNULL,timeout=timeout)
    log.append('$ '+' '.join(map(str,args))+'\n'+p.stdout+p.stderr)
    (public/'iso-assembly-0.1.3.log').write_text('\n'.join(log))
    if p.returncode:
        print(p.stdout[-2000:]+p.stderr[-3000:],flush=True)
        raise RuntimeError(args)
    return p.stdout

ks=b/'domLight-0.1.3-x86_64.ks'
urllib.request.urlretrieve('http://192.168.64.1:8765/cloud-flex-port/'+ks.name,ks)
Path('/tmp/domlight-admin.ks').write_text('user --name=validation --groups=wheel --iscrypted --password=invalid\n')
run(['ksvalidator','-v','F44',ks]);Path('/tmp/domlight-admin.ks').unlink()

# Preserve Fedora's group definitions so @core resolves from the USB alone.
origin='https://dl.fedoraproject.org/pub/fedora/linux/releases/44/Everything/x86_64/os/'
md=ET.fromstring(urllib.request.urlopen(origin+'repodata/repomd.xml').read())
ns={'r':'http://linux.duke.edu/metadata/repo'}
group=next(x for x in md.findall('r:data',ns) if x.attrib['type']=='group')
href=group.find('r:location',ns).attrib['href']
blob=urllib.request.urlopen(origin+href).read()
checksum=group.find('r:checksum',ns)
assert hashlib.new(checksum.attrib['type'],blob).hexdigest()==checksum.text
# Fedora group metadata may be compressed even under the 'group' data type.
if blob.startswith(b'\x1f\x8b'):
    import gzip;blob=gzip.decompress(blob)
elif blob.startswith(b'BZh'):
    import bz2;blob=bz2.decompress(blob)
elif blob.startswith(b'\xfd7zXZ'):
    import lzma;blob=lzma.decompress(blob)
elif blob.startswith(b'\x28\xb5\x2f\xfd'):
    from compression import zstd
    blob=zstd.decompress(blob)
ET.fromstring(blob)
comps=b/'comps.xml';comps.write_bytes(blob)
run(['createrepo_c','--groupfile',comps,repo])

# Resolve again with only the USB repository enabled, against an empty root.
section=ks.read_text().split('%packages --exclude-weakdeps\n',1)[1].split('%end',1)[0]
roots=[line for line in section.splitlines() if line and not line.startswith(('#','-'))]
run(['sudo','dnf','--releasever=44','--forcearch=x86_64',
     '--installroot='+str(b/'offline-check-root'),'--use-host-config',
     '--disable-repo=*','--repofrompath=domlight-offline,file://'+str(repo),
     '--setopt=install_weak_deps=False','--exclude=dolphin',
     'install','-y','--downloadonly',*roots])

# Verify every RPM against Fedora's key or the existing domLight signing key.
key=b/'RPM-GPG-KEY-cloud-flex'
urllib.request.urlretrieve('http://192.168.64.1:8765/domLight/docs/RPM-GPG-KEY-cloud-flex',key)
db=Path(run(['sudo','mktemp','-d','/var/lib/domlight-verify-XXXXXX']).strip())
try:
    run(['sudo','chcon','--reference=/usr/lib/sysimage/rpm',db])
    run(['sudo','rpmdb','--dbpath',db,'--initdb'])
    run(['sudo','rpmkeys','--dbpath',db,'--import','/etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-44-primary',key])
    run(['sudo','rpmkeys','--dbpath',db,'--checksig',*sorted((repo/'Packages').glob('*.rpm'))])
finally:
    run(['sudo','rm','-rf','--',db])

# Build an actual package tree, retaining the matching Fedora stage2 image.
tree=b/'.treeinfo'
urllib.request.urlretrieve('http://192.168.64.1:8765/cloud-flex-port/fedora44.treeinfo',tree)
cfg=configparser.ConfigParser();cfg.read(tree)
cfg.remove_option('checksums','images/boot.iso')
with tree.open('w') as f:cfg.write(f)

extract=b/'boot';extract.mkdir(exist_ok=True)
for source,name in [('/EFI/BOOT/grub.cfg','uefi.cfg'),('/boot/grub2/grub.cfg','bios.cfg')]:
    p=extract/name
    if p.exists():p.unlink()
    run(['xorriso','-osirrox','on','-indev',base,'-extract',source,p])
with base.open('rb') as f:
    f.seek(2350452*512);(extract/'efi.img').write_bytes(f.read(26480*512))
fat=extract/'fat.cfg'
if fat.exists():fat.unlink()
run(['mcopy','-i',extract/'efi.img','::/EFI/BOOT/grub.cfg',fat])
for name in ['uefi.cfg','bios.cfg','fat.cfg']:
    p=extract/name
    lines=[]
    for line in p.read_text().splitlines():
        if re.match(r'\s*(linux|linuxefi|append)\s',line):
            line+=' inst.ks=hd:LABEL=Fedora-E-dvd-x86_64-44:/cloud-flex-x86_64.ks'
        lines.append(line)
    p.write_text('\n'.join(lines)+'\n')
run(['mcopy','-o','-i',extract/'efi.img',fat,'::/EFI/BOOT/grub.cfg'])

# Keep the custom signed packages in their dedicated installation repository too.
custom=b/'cloud-flex';custom.mkdir(exist_ok=True)
for name in ['cloud-flex-desktop-0.1.1-1.fc44.noarch.rpm','cloud-flex-release-0.1.0-1.fc44.noarch.rpm']:
    shutil.copy2(repo/'Packages'/name,custom/name)
run(['createrepo_c',custom])
output=home/'.cache/cloud-flex-build/domLight-0.1.3-Fedora44-x86_64-offline.iso'
output.parent.mkdir(parents=True,exist_ok=True)
if output.exists():output.unlink()
run(['xorriso','-indev',base,'-outdev',output,'-boot_image','any','replay',
     '-map',ks,'/cloud-flex-x86_64.ks','-map',custom,'/cloud-flex',
     '-map',repo/'Packages','/Packages','-map',repo/'repodata','/repodata',
     '-map',tree,'/.treeinfo','-map',public/'package-manifest.json','/domLight-package-manifest.json',
     '-map',extract/'uefi.cfg','/EFI/BOOT/grub.cfg','-map',extract/'bios.cfg','/boot/grub2/grub.cfg',
     '-append_partition','2','0xef',extract/'efi.img','-commit','-end'])
run(['implantisomd5','--force',output]);run(['checkisomd5',output])
run(['xorriso','-indev',output,'-report_el_torito','plain','-report_system_area','plain'])
link=public/output.name
if link.is_symlink() or link.exists():link.unlink()
link.symlink_to(output)
print('ISO_READY',output,hashlib.file_digest(output.open('rb'),'sha256').hexdigest(),flush=True)
