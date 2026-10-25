# domLight

Lightweight Fedora 44 desktop for Google web apps and basic browsing, with shared desktop assets for x86-64 and ARM64.

## Status

Initial x86-64 network installer built. Signed update feed is being prepared; this repository is not yet ready for client enrollment.

## Update publishing

The `tools/` scripts build the repository configuration package, sign desktop RPMs and repository metadata, and generate the enrollment script. Run signing on the private Fedora build machine. Only public keys, signed packages and generated metadata belong in the published feed.

Private signing keys, account profiles, credentials and VM disks must never be committed.

Updates cover `cloud-flex-desktop` and `cloud-flex-release`. Fedora continues to supply operating system packages. Desktop configuration migrations require explicit versioned changes; package updates do not overwrite existing user preferences.

## Installer

The initial ISO is a network installer for Intel/AMD PCs and needs internet access. Disk selection and user creation remain interactive. Physical hardware boot testing is pending.
