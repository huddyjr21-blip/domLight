Name: cloud-flex-desktop
Version: 0.1.1
Release: 1%{?dist}
Summary: Lightweight cloud desktop customization for Fedora Plasma
License: MIT
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch
Requires: python3
Requires: python3-pyqt6
Requires: plasma-desktop
Requires: plasma-workspace
Requires: kwin
Requires: plasma-breeze
Requires: plasma-integration
Requires: plasma-systemsettings
Requires: pipewire-pulseaudio
Requires: wireplumber
Requires: breeze-icon-theme
Requires: plasma-nm
Requires: plasma-pa
Requires: powerdevil
Requires: qt6-qttools
Requires: pulseaudio-utils
Requires: NetworkManager
Requires: chromium
Obsoletes: dolphin
Requires: nemo
Requires: gsettings-desktop-schemas
Requires: konsole
Requires: pam-kwallet
Requires: google-noto-sans-fonts
Requires: google-noto-sans-mono-fonts
Requires: xdg-utils

%description
Portable Plasma launcher, quick settings, system settings, window decoration,
web app launchers and appearance defaults. Supports Fedora x86_64 and aarch64.
User settings are changed only by explicitly running the setup command.
No Google profiles, credentials, Wallet files or Drive mount are included.

%prep
%setup -q

%build

%install
mkdir -p %{buildroot}/usr/share
cp -a root/usr/share/. %{buildroot}/usr/share/

%files
/usr/share/cloud-flex
/usr/share/applications/cloud-*.desktop
/usr/share/plasma/plasmoids/local.cloud.flex.*
/usr/share/plasma/desktoptheme/cloud-flex-bubbles
/usr/share/aurorae/themes/CloudFlexWindows
/usr/share/color-schemes/CloudFlex.colors
/usr/share/themes/CloudFlexNemo

/usr/share/autostart/cloud-flex-nemo.desktop
