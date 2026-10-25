# domLight 0.1.5 Fedora 44 x86_64 online installer.
# Native account creation, automatic desktop package selection and appearance setup.
# Disk selection remains interactive.
graphical
lang en_US.UTF-8
keyboard us
timezone America/New_York --utc
rootpw --lock
selinux --enforcing
firewall --enabled
url --url=https://dl.fedoraproject.org/pub/fedora/linux/releases/44/Everything/x86_64/os/
repo --name=updates --baseurl=https://dl.fedoraproject.org/pub/fedora/linux/updates/44/Everything/x86_64/
repo --name=cloud-flex --baseurl=file:///run/install/repo/cloud-flex/
services --enabled=NetworkManager,sddm
xconfig --startxonboot

%packages --exclude-weakdeps
@core
kernel
kernel-modules
kernel-modules-extra
linux-firmware
linux-firmware-whence
realtek-firmware
atheros-firmware
brcmfmac-firmware
iwlwifi-mvm-firmware
iwlwifi-dvm-firmware
mt7xxx-firmware
intel-gpu-firmware
amd-gpu-firmware
nvidia-gpu-firmware
intel-audio-firmware
alsa-sof-firmware
alsa-ucm
microcode_ctl
amd-ucode-firmware
pciutils
usbutils
rfkill
ethtool
NetworkManager-wifi
sddm
sddm-breeze
sddm-wayland-plasma
mesa-dri-drivers
mesa-vulkan-drivers
qt6-qtwayland
xorg-x11-server-Xwayland
bluez
bluez-obexd
bluedevil
alsa-utils
sudo
# Required for SDDM/Plasma session runtime directories; not a weak dependency here.
systemd-pam
cloud-flex-desktop
-dolphin
cloud-flex-release
grub2-efi-x64
shim-x64
efibootmgr
grub2-pc
grub2-tools
btrfs-progs
%end

%post --interpreter=/usr/bin/bash --erroronfail --log=/var/log/domlight-install.log
set -eu
# Keep native Anaconda account creation, sudo policy and bootloader handling.
# Apply only the packaged appearance defaults, without running a user session.
python3 - <<'PYDEFAULTS'
import os,pwd,shutil
from pathlib import Path
source=Path('/usr/share/cloud-flex/defaults')
targets=[(Path('/etc/skel'),0,0)]
targets += [(Path(u.pw_dir),u.pw_uid,u.pw_gid) for u in pwd.getpwall()
            if 1000 <= u.pw_uid < 60000 and u.pw_dir.startswith('/home/') and Path(u.pw_dir).is_dir()]
for home,uid,gid in targets:
    config=home/'.config'
    config.mkdir(parents=True,exist_ok=True)
    os.chown(config,uid,gid)
    for template in source.iterdir():
        if template.is_file():
            dest=config/template.name
            shutil.copyfile(template,dest)
            os.chmod(dest,0o644)
            os.chown(dest,uid,gid)
PYDEFAULTS
systemctl enable --force sddm.service
systemctl set-default graphical.target
systemctl enable cloud-flex-update.timer
%end
