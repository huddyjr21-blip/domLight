"""Remaster the known Fedora netinstaller with automatic domLight package setup."""
from pathlib import Path
import subprocess,urllib.request,hashlib,json,tempfile,struct,re
h=Path.home();b=h/'.cache/domlight-online-0.1.5';b.mkdir(exist_ok=True)
p=Path('/tmp/domlight-0.1.5-build');p.mkdir(exist_ok=True)
source=h/'.cache/cloud-flex-build/domLight-0.1.2-Fedora44-x86_64-netinst.iso'
assert hashlib.file_digest(source.open('rb'),'sha256').hexdigest()=='317f2b0d148cfb7de7048c4e638c5f370dfbe17e67ee58e6d93349a00cfeb165'
log=[]
def run(args):
 r=subprocess.run(list(map(str,args)),capture_output=True,text=True,timeout=600)
 log.append('$ '+' '.join(map(str,args))+'\n'+r.stdout+r.stderr)
 (p/'assembly.log').write_text('\n'.join(log))
 if r.returncode:raise RuntimeError(r.stdout[-1500:]+r.stderr[-2500:])
 return r.stdout
ks=b/'domLight-0.1.5-x86_64.ks'
urllib.request.urlretrieve('http://192.168.64.1:8765/cloud-flex-port/'+ks.name,ks)
s=ks.read_text()
assert '\nsystemd-pam\n' in s
assert '%pre' not in s and '%include' not in s and '\nuser ' not in s
assert '\ncdrom\n' not in s and '\nurl --url=https://' in s
assert not any(x.startswith(('clearpart','autopart','zerombr','part ')) for x in s.splitlines())
run(['ksvalidator','-v','F44',ks])
post=s.split('%post --interpreter=/usr/bin/bash --erroronfail --log=/var/log/domlight-install.log\n')[1].split('%end')[0]
postfile=b/'post.sh';postfile.write_text(post);run(['bash','-n',postfile])
compile(post.split("<<'PYDEFAULTS'\n")[1].split('\nPYDEFAULTS')[0],'<appearance-setup>','exec')
output=h/'.cache/cloud-flex-build/domLight-0.1.5-Fedora44-x86_64-online.iso'
if output.exists():output.unlink()
run(['xorriso','-indev',source,'-outdev',output,'-boot_image','any','replay','-map',ks,'/cloud-flex-x86_64.ks','-commit','-end'])
run(['implantisomd5','--force',output]);run(['checkisomd5',output])
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
  f.seek(first*512);efi=td/'efi.img';efi.write_bytes(f.read((last-first+1)*512))
 fat=td/'fat.cfg';run(['mcopy','-i',efi,'::/EFI/BOOT/grub.cfg',fat])
 assert 'inst.ks=hd:LABEL=Fedora-E-dvd-x86_64-44:/cloud-flex-x86_64.ks' in fat.read_text()
 run(['xorriso','-osirrox','on','-indev',output,'-extract','/cloud-flex',td/'repo'])
 expected={'cloud-flex-desktop-0.1.1-1.fc44.noarch.rpm':'b921d22c004910663cf3f4f3942980137274427ce9fb40401c7f1a7a86ee22aa','cloud-flex-release-0.1.0-1.fc44.noarch.rpm':'4633a9b4f80cfb48cb07a6aa652749bfe0a939418bd07a5e8a44debc2c3cdc50'}
 for name,sha in expected.items():
  assert hashlib.file_digest((td/'repo'/name).open('rb'),'sha256').hexdigest()==sha
report={'version':'0.1.5','installation':'online Fedora packages, embedded signed domLight packages, automatic appearance and update enrollment','account_and_storage':'native interactive; no default credentials or automatic disk erasure','kickstart_validation':'PASS','post_shell_and_python_syntax':'PASS','media_check':'PASS','boot_configs':'BIOS and both UEFI configurations checked','embedded_packages':'match published signed desktop 0.1.1 and release 0.1.0','full_install_tested':False,'physical_hardware_boot_tested':False,'bytes':output.stat().st_size,'sha256':hashlib.file_digest(output.open('rb'),'sha256').hexdigest()}
(p/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
link=p/output.name
if link.exists() or link.is_symlink():link.unlink()
link.symlink_to(output)
print(json.dumps(report,indent=2),flush=True)
