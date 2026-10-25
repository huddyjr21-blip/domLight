"""Replace the failing pre-install wizard with native Anaconda account creation."""
from pathlib import Path
import subprocess,urllib.request,hashlib,json,tempfile,struct,re
h=Path.home();b=h/'.cache/domlight-offline-0.1.4';b.mkdir(exist_ok=True)
p=Path('/tmp/domlight-0.1.4-build');p.mkdir(exist_ok=True)
source=h/'.cache/cloud-flex-build/domLight-0.1.3-Fedora44-x86_64-offline.iso'
assert hashlib.file_digest(source.open('rb'),'sha256').hexdigest()=='8af647c51c790ea1630a6a2b56c820a1099343ed51b1a37cf9525419be24c9b0'
log=[]
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=600)
 log.append('$ '+' '.join(map(str,args))+'\n'+r.stdout+r.stderr)
 (p/'iso-assembly-0.1.4.log').write_text('\n'.join(log))
 if r.returncode:raise RuntimeError(r.stdout[-1500:]+r.stderr[-2500:])
 return r.stdout
ks=b/'domLight-0.1.4-x86_64.ks';urllib.request.urlretrieve('http://192.168.64.1:8765/cloud-flex-port/'+ks.name,ks)
s=ks.read_text()
assert '%pre' not in s and '%include' not in s and 'chvt' not in s and 'clear\n' not in s
assert 'rootpw --lock' in s and 'No usable administrator account created' in s
assert '\nuser ' not in s and '\ncdrom\n' in s
assert not any(x.startswith(('clearpart','autopart','zerombr','part ')) for x in s.splitlines())
run(['ksvalidator','-v','F44',ks])
post=s.split('%post --erroronfail --log=/var/log/cloud-flex-install.log\n')[1].split('%end')[0]
postfile=b/'post.sh';postfile.write_text(post);run(['bash','-n',postfile])
# Check native Anaconda's user screen in the actual installer runtime.
w=h/'.cache/domlight-stage2-check';u=w/'usr/bin/unsquashfs'
user=run([u,'-cat',w/'install.img','usr/lib64/python3.14/site-packages/pyanaconda/ui/gui/spokes/user.py'])
assert 'return not self._users_module.CheckAdminUserExists()' in user
assert 'return bool(get_user_list(self._users_module))' in user
# No Kickstart user has been supplied: native GUI user spoke is enabled and mandatory.
assert 'if environment == constants.ANACONDA_ENVIRON:\n            return True' in user
output=h/'.cache/cloud-flex-build/domLight-0.1.4-Fedora44-x86_64-offline.iso'
if output.exists():output.unlink()
run(['xorriso','-indev',source,'-outdev',output,'-boot_image','any','replay','-map',ks,'/cloud-flex-x86_64.ks','-commit','-end'])
run(['implantisomd5','--force',output]);run(['checkisomd5',output])
run(['xorriso','-indev',output,'-report_el_torito','plain','-report_system_area','plain'])
with tempfile.TemporaryDirectory(dir=b) as td:
 td=Path(td)
 def extract(path):
  dest=td/Path(path).name
  if dest.exists():dest.unlink()
  run(['xorriso','-osirrox','on','-indev',output,'-extract',path,dest]);return dest
 assert extract('/cloud-flex-x86_64.ks').read_text()==s
 for path in ['/EFI/BOOT/grub.cfg','/boot/grub2/grub.cfg']:
  lines=[l for l in extract(path).read_text().splitlines() if re.match(r'\s*(linux|linuxefi)\s',l)]
  assert lines and all('inst.ks=hd:LABEL=Fedora-E-dvd-x86_64-44:/cloud-flex-x86_64.ks' in l for l in lines)
 with output.open('rb') as f:
  f.seek(512);hdr=f.read(92);assert hdr[:8]==b'EFI PART'
  table=struct.unpack_from('<Q',hdr,72)[0];size=struct.unpack_from('<I',hdr,84)[0]
  f.seek(table*512+size);entry=f.read(size);first,last=struct.unpack_from('<QQ',entry,32)
  assert entry[:16].hex()=='28732ac11ff8d211ba4b00a0c93ec93b'
  f.seek(first*512);efi=td/'efi.img';efi.write_bytes(f.read((last-first+1)*512))
 fat=td/'fat.cfg';run(['mcopy','-i',efi,'::/EFI/BOOT/grub.cfg',fat]);assert 'inst.ks=' in fat.read_text()
 # Confirm complete offline RPM tree and metadata are retained exactly.
 manifest=json.loads(extract('/domLight-package-manifest.json').read_text())
 run(['xorriso','-osirrox','on','-indev',output,'-extract','/Packages',td/'Packages'])
 for package in manifest:
  original=h/'.cache/domlight-offline-0.1.3/repo/Packages'/package['file']
  copy=td/'Packages'/package['file']
  assert hashlib.file_digest(original.open('rb'),'sha256').digest()==hashlib.file_digest(copy.open('rb'),'sha256').digest()
 assert len(manifest)==922
 for rel in ['repodata/repomd.xml']:
  assert extract('/'+rel).read_bytes()==(h/'.cache/domlight-offline-0.1.3/repo'/rel).read_bytes()
report={'version':'0.1.4','account_setup':'native Anaconda user screen; custom pre-install script and include removed','administrator_guard':'locked root, native mandatory account screen, post-install wheel/password verification','offline_packages_verified_identical':922,'media_check':'PASS','boot_configs':'BIOS, root UEFI and appended EFI verified','kickstart_validation':'PASS','post_script_syntax':'PASS','physical_hardware_boot_tested':False,'full_install_tested':False,'bytes':output.stat().st_size,'sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest()}
(p/'iso-verification-0.1.4.json').write_text(json.dumps(report,indent=2))
link=p/output.name
if link.is_symlink() or link.exists():link.unlink()
link.symlink_to(output)
print(json.dumps(report,indent=2),flush=True)
