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

## Installer 0.1.2

The rebuilt x86-64 network installer requires choosing an administrator username and password (12 characters minimum) before disk selection. It refuses installation completion if no usable wheel-group account exists. The sudo policy is validated, SDDM is explicitly enabled, Plasma Wayland login and Mesa drivers are included, and Nemo is the file manager. Signed desktop updates are enrolled automatically. Disk selection remains interactive.

Use `domLight-0.1.2-Fedora44-x86_64-netinst.iso`, not the old 0.1.0 installer. Checksums and installer sources are in `installer/`. Media integrity, boot configurations, embedded package, wizard input validation and hashing were checked. Full installation and physical graphics startup still need hardware testing.

## Earlier installer limitations

The initial ISO is an Intel/AMD network installer requiring internet access. Disk selection and user creation remain interactive. This ISO predates repository enrollment; run the command above after installation. Physical hardware boot testing is pending.

The original ARM development VM has user-local theme/widget overrides; migrate those before enrolling it so they do not shadow packaged updates. Fresh ISO installations use system assets.
