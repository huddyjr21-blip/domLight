"""Architecture-independent ISO remaster; preserves original bootloader binaries."""
from pathlib import Path
import urllib.request,subprocess,hashlib,shutil,re,json
b=Path('/tmp/cloud-flex-iso');b.mkdir(exist_ok=True)
log=[]
def run(args):
 r=subprocess.run([str(a) for a in args],capture_output=True,text=True,stdin=subprocess.DEVNULL,timeout=120);log.append('$ '+' '.join(map(str,args))+'\n'+r.stdout+r.stderr)
 (b/'assembly.log').write_text('\n'.join(log))
 if r.returncode:print(r.stderr[-2500:]);raise RuntimeError(str(args))
 return r.stdout+r.stderr
if not all(shutil.which(x) for x in ['xorriso','mcopy','createrepo_c','ksvalidator','implantisomd5']):
 run(['sudo','dnf','install','-y','--setopt=install_weak_deps=false','xorriso','mtools','createrepo_c','pykickstart','isomd5sum'])
iso=b/'fedora-base.iso'
if not iso.exists():urllib.request.urlretrieve('http://192.168.64.1:8765/fedora-base.iso',iso)
assert hashlib.file_digest(iso.open('rb'),'sha256').hexdigest()=='bd285201494dd0ba09b54d05ac707de1401668b8512a573edb5922dcf9d7067e'
repo=b/'cloud-flex';repo.mkdir(exist_ok=True)
rpm='cloud-flex-desktop-0.1.1-1.fc44.noarch.rpm'
for old in repo.glob('*.rpm'):old.unlink()
urllib.request.urlretrieve('http://192.168.64.1:8765/domLight/docs/fedora/44/noarch/Packages/'+rpm,repo/rpm)
release='cloud-flex-release-0.1.0-1.fc44.noarch.rpm'
urllib.request.urlretrieve('http://192.168.64.1:8765/domLight/docs/fedora/44/noarch/Packages/'+release,repo/release)
ks=b/'cloud-flex-x86_64.ks';urllib.request.urlretrieve('http://192.168.64.1:8765/cloud-flex-port/domLight-0.1.2-x86_64.ks',ks)
Path('/tmp/domlight-admin.ks').write_text('user --name=validation --groups=wheel --iscrypted --password=invalid\n')
run(['ksvalidator','-v','F44',ks])
Path('/tmp/domlight-admin.ks').unlink()
run(['createrepo_c',repo])
extract=b/'extracted';extract.mkdir(exist_ok=True)
for source,name in [('/EFI/BOOT/grub.cfg','grub.cfg'),('/boot/grub2/grub.cfg','bios-grub.cfg')]:
 run(['xorriso','-osirrox','on','-indev',iso,'-extract',source,extract/name])
with iso.open('rb') as f:
 f.seek(2350452*512);(extract/'efiboot.img').write_bytes(f.read(26480*512))
# Add an explicit kickstart to each installer kernel entry; leave storage interactive.
for name in ['grub.cfg','bios-grub.cfg']:
 p=extract/name;t=p.read_text();lines=[]
 for line in t.splitlines():
  if re.match(r'\s*(linux|linuxefi|append)\s',line):
   line+=' inst.ks=hd:LABEL=Fedora-E-dvd-x86_64-44:/cloud-flex-x86_64.ks'
  lines.append(line)
 p.write_text('\n'.join(lines)+'\n')
# EFI FAT image has its own boot configuration on USB media.
fatcfg=extract/'fat-grub.cfg'
if fatcfg.exists():fatcfg.unlink()
run(['mcopy','-o','-i',extract/'efiboot.img','::/EFI/BOOT/grub.cfg',fatcfg])
t=fatcfg.read_text();lines=[]
for line in t.splitlines():
 if re.match(r'\s*(linux|linuxefi)\s',line):line+=' inst.ks=hd:LABEL=Fedora-E-dvd-x86_64-44:/cloud-flex-x86_64.ks'
 lines.append(line)
fatcfg.write_text('\n'.join(lines)+'\n')
run(['mcopy','-o','-i',extract/'efiboot.img',fatcfg,'::/EFI/BOOT/grub.cfg'])
publish=Path('/tmp/cloud-flex-export')
output=Path.home()/'.cache/cloud-flex-build/domLight-0.1.2-Fedora44-x86_64-netinst.iso'
output.parent.mkdir(parents=True,exist_ok=True)
if output.exists():output.unlink()
run(['xorriso','-indev',iso,'-outdev',output,'-boot_image','any','replay','-map',ks,'/cloud-flex-x86_64.ks','-map',repo,'/cloud-flex','-map',extract/'grub.cfg','/EFI/BOOT/grub.cfg','-map',extract/'bios-grub.cfg','/boot/grub2/grub.cfg','-append_partition','2','0xef',extract/'efiboot.img','-commit','-end'])
run(['implantisomd5','--force',output])
run(['checkisomd5',output])
run(['xorriso','-indev',output,'-report_el_torito','plain','-report_system_area','plain'])
shutil.copy2(b/'assembly.log',publish/'iso-assembly.log')
link=publish/output.name
if link.is_symlink() or link.exists():link.unlink()
link.symlink_to(output)
print('ISO ready:',output.name,hashlib.file_digest(output.open('rb'),'sha256').hexdigest())
