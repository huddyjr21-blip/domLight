# domLight

Lightweight Fedora 44 desktop for Google web apps and basic browsing. Signed updates share desktop assets across x86-64 and ARM64.

## Latest update: 0.1.1

Replaces Dolphin with Nemo, updates the Files launcher and default folder handler, and applies the Nemo theme at next sign-in. A one-time migration backs up affected user configuration.

## Enroll a test machine

Run once after installing the initial ISO, from a terminal on the Fedora test machine:

```bash
curl --fail --location https://huddyjr21-blip.github.io/domLight/enroll.sh -o enroll-domlight.sh
less enroll-domlight.sh
bash enroll-domlight.sh
```

The script verifies the pinned public-key checksum, checks the enrollment RPM signature, installs repository configuration and enables daily desktop updates. Both RPM signatures and repository metadata signatures are required. It targets Fedora 44 x86-64/aarch64 with the domLight desktop package already installed. It never forces a reboot. Sign out and back in after desktop updates.

Manual update:

```bash
sudo systemctl start cloud-flex-update.service
journalctl -u cloud-flex-update.service -n 30
```

Disable automatic checks:

```bash
sudo systemctl disable --now cloud-flex-update.timer
```

Updates cover `cloud-flex-desktop` and `cloud-flex-release`. Fedora supplies operating-system updates separately. Existing user preferences are not reset automatically.

Signing fingerprint: `9F8C932CE936A621EA9A154B9132D5D869E228F3`.

## Publish an update

1. Bump the desktop RPM version/release, rebuild and test it on a test machine. Keep the same NEVRA immutable.
2. On the private Fedora signing VM, clone/pull this repository and set `GNUPGHOME=$HOME/.local/share/domlight-signing/gnupg`.
3. Run `python3 tools/publish.py --root docs --key 9F8C932CE936A621EA9A154B9132D5D869E228F3 /path/to/new-desktop.noarch.rpm`. Enter the signing passphrase when prompted. Fedora build tools `rpm-build rpm-sign createrepo_c gnupg2` are required. Administrator access is used only for an isolated verification database with Fedora SELinux labels.
4. Review `git diff`, commit the updated `docs/` files and push to `main`. GitHub Pages publishes from `main:/docs`; enrolled machines check daily.

Keep old package versions for manual recovery. If the repository config or timer changes, bump and rebuild `cloud-flex-release` too; the initial generator is under `tools/make-release.py`. User configuration changes need explicit tested migrations.

The private signing key and its revocation certificate remain in the private Fedora VM. Keep an encrypted offline backup of that signing directory and preserve the passphrase. Never commit private keys, browser profiles, credentials or VM disks. The key expires October 24, 2028; plan renewal before then.

## Installer 0.1.3

Use `domLight-0.1.3-Fedora44-x86_64-offline.iso` for Intel/AMD PCs. This replaces the previous network installers and contains the complete desktop installation package set; setup needs no internet connection. It explicitly includes common Wi-Fi, Bluetooth, graphics and audio firmware, standard/extra kernel modules, CPU microcode and hardware diagnostic tools. The Realtek RTL8821CE Wi-Fi/Bluetooth and Intel Apollo Lake SOF firmware files reported missing on the KAMRUI test PC were verified in the image.

The installer requires an administrator account (password at least 12 characters), validates sudo access, enables graphical login, uses Nemo, and enrolls signed desktop updates. Disk selection remains interactive. No default credentials or automatic disk erasure are configured.

The 2.62 GB image was checked for USB-local dependency closure, all 922 RPM signatures, repository checksums, firmware paths, BIOS/UEFI configurations and media integrity. Full installation and physical GPU startup remain untested; the earlier black screen is not yet confirmed resolved. Sources, manifest, checksum and optional offline repair instructions for existing installations are in `installer/`. The ISO binary is distributed separately.

## Earlier installer limitations

The initial ISO is an Intel/AMD network installer requiring internet access. Disk selection and user creation remain interactive. This ISO predates repository enrollment; run the command above after installation. Physical hardware boot testing is pending.

The original ARM development VM has user-local theme/widget overrides; migrate those before enrolling it so they do not shadow packaged updates. Fresh ISO installations use system assets.
