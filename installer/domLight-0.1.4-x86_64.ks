# domLight 0.1.4 Fedora 44 x86_64 offline installer.
# Use native Anaconda user creation and administrator validation.
# Disk selection remains interactive.
graphical
lang en_US.UTF-8
keyboard us
timezone America/New_York --utc
rootpw --lock
selinux --enforcing
firewall --enabled
cdrom
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

%post --erroronfail --log=/var/log/cloud-flex-install.log
set -euo pipefail
printf '%%wheel ALL=(ALL) ALL\n' >/etc/sudoers.d/90-domlight-admin
chmod 0440 /etc/sudoers.d/90-domlight-admin
visudo -cf /etc/sudoers
systemctl enable --force sddm.service
systemctl set-default graphical.target
test -e /usr/share/wayland-sessions/plasma.desktop
test "$(readlink -f /etc/systemd/system/display-manager.service)" = /usr/lib/systemd/system/sddm.service
python3 - <<'PYCHECK'
import grp,pwd
from pathlib import Path
shadow={r.split(":",2)[0]:r.split(":",2)[1] for r in Path("/etc/shadow").read_text().splitlines()}
admins=set(grp.getgrnam("wheel").gr_mem)
assert any(u.pw_uid>=1000 and u.pw_name in admins and shadow.get(u.pw_name,"!") not in ["", "!", "!!", "*"] and not shadow.get(u.pw_name,"!").startswith("!") for u in pwd.getpwall()), "No usable administrator account created"
PYCHECK
# Verify hardware support is actually installed; fail before declaring success.
rpm -q kernel-modules kernel-modules-extra realtek-firmware alsa-sof-firmware intel-gpu-firmware pciutils
find /usr/lib/firmware -path '*/rtw88/rtw8821c_fw.bin*' -print -quit | grep -q .
find /usr/lib/firmware -path '*/rtl_bt/rtl8821c_fw.bin*' -print -quit | grep -q .
find /usr/lib/firmware -path '*/sof-apl.ri*' -print -quit | grep -q .
systemctl enable cloud-flex-update.timer
python3 /usr/share/cloud-flex/setup.py --apply --offline --home /etc/skel
python3 - <<'PYSETUP'
import pwd,subprocess,os
from pathlib import Path
for user in pwd.getpwall():
 if 1000 <= user.pw_uid < 60000 and user.pw_dir.startswith('/home/'):
  home=Path(user.pw_dir)
  if not home.is_dir():continue
  subprocess.run(['python3','/usr/share/cloud-flex/setup.py','--apply','--offline','--home',str(home)],check=True)
  for rel in ['.config','.local/state/cloud-flex']:
   root=home/rel
   if root.exists():
    os.chown(root,user.pw_uid,user.pw_gid)
    for parent,dirs,files in os.walk(root):
     for name in dirs+files:os.chown(Path(parent)/name,user.pw_uid,user.pw_gid,follow_symlinks=False)
PYSETUP
%end
