from pathlib import Path
import subprocess,tempfile,hashlib,json,re,struct,xml.etree.ElementTree as ET

home=Path.home();work=home/'.cache/domlight-offline-0.1.3'
iso=home/'.cache/cloud-flex-build/domLight-0.1.3-Fedora44-x86_64-offline.iso'
public=Path('/tmp/domlight-0.1.3-export')
report={'hardware_boot_tested':False,'full_install_tested':False}
with tempfile.TemporaryDirectory(dir=home/'.cache') as folder:
    folder=Path(folder)
    def extract(path):
        dest=folder/Path(path).name
        if dest.exists():dest.unlink()
        subprocess.run(['xorriso','-osirrox','on','-indev',str(iso),'-extract',path,str(dest)],check=True,capture_output=True)
        return dest
    ks=extract('/cloud-flex-x86_64.ks').read_text()
    assert '\ncdrom\n' in ks and '\nurl ' not in ks and 'https://' not in ks
    for token in ['%include /tmp/domlight-admin.ks','--groups=wheel','systemctl enable --force sddm.service','systemctl set-default graphical.target','set -euo pipefail','realtek-firmware','alsa-sof-firmware','intel-gpu-firmware','kernel-modules-extra','pciutils','-dolphin']:
        assert token in ks,token
    assert not any(l.startswith(('clearpart','autopart','zerombr','part ')) for l in ks.splitlines())
    for path in ['/EFI/BOOT/grub.cfg','/boot/grub2/grub.cfg']:
        lines=[l for l in extract(path).read_text().splitlines() if re.match(r'\s*(linux|linuxefi)\s',l)]
        assert lines and all('inst.ks=' in l for l in lines)
    manifest=json.loads(extract('/domLight-package-manifest.json').read_text())
    names={p['name'] for p in manifest}
    for name in ['kernel','kernel-core','kernel-modules','kernel-modules-extra','realtek-firmware','alsa-sof-firmware','intel-gpu-firmware','amd-gpu-firmware','atheros-firmware','brcmfmac-firmware','mt7xxx-firmware','iwlwifi-mvm-firmware','NetworkManager-wifi','sddm-wayland-plasma','mesa-dri-drivers','cloud-flex-desktop','cloud-flex-release','nemo','pciutils']:
        assert name in names,name
    assert 'dolphin' not in names
    report['offline_packages']=len(manifest)
    md=ET.fromstring(extract('/repodata/repomd.xml').read_bytes())
    ns={'r':'http://linux.duke.edu/metadata/repo'}
    assert any(d.attrib['type']=='group' for d in md.findall('r:data',ns))
    for d in md.findall('r:data',ns):
        loc=d.find('r:location',ns).attrib['href'];checksum=d.find('r:checksum',ns)
        assert hashlib.new(checksum.attrib['type'],extract('/'+loc).read_bytes()).hexdigest()==checksum.text
    firmware_paths={}
    for name,required in [('realtek-firmware',['rtw88/rtw8821c_fw.bin','rtl_bt/rtl8821c_fw.bin']),('alsa-sof-firmware',['sof-apl.ri'])]:
        package=next(p for p in manifest if p['name']==name)
        rpm=extract('/Packages/'+package['file'])
        files=subprocess.check_output(['rpm','-qpl',str(rpm)],text=True)
        for path in required:assert path in files,path
        firmware_paths[name]=required
    report['required_device_firmware']=firmware_paths
    rpm=extract('/cloud-flex/cloud-flex-desktop-0.1.1-1.fc44.noarch.rpm')
    assert rpm.read_bytes()==(work/'repo/Packages'/rpm.name).read_bytes()
    with iso.open('rb') as f:
        f.seek(512);hdr=f.read(92);assert hdr[:8]==b'EFI PART'
        table=struct.unpack_from('<Q',hdr,72)[0];size=struct.unpack_from('<I',hdr,84)[0]
        f.seek(table*512+size);entry=f.read(size);first,last=struct.unpack_from('<QQ',entry,32)
        assert entry[:16].hex()=='28732ac11ff8d211ba4b00a0c93ec93b'
        f.seek(first*512);efi=folder/'efi.img';efi.write_bytes(f.read((last-first+1)*512))
    fat=folder/'fat.cfg'
    subprocess.run(['mcopy','-i',str(efi),'::/EFI/BOOT/grub.cfg',str(fat)],check=True,capture_output=True)
    assert 'inst.ks=' in fat.read_text()
report['boot_configurations']='BIOS and both UEFI paths checked'
report['installation_source']='USB-local repository with Fedora core group metadata'
report['sha256']=hashlib.file_digest(iso.open('rb'),'sha256').hexdigest()
report['bytes']=iso.stat().st_size
(public/'iso-verification-0.1.3.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2),flush=True)
