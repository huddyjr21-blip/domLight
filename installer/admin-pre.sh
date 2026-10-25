#!/bin/bash
set -euo pipefail
# Use a dedicated console, then return to the installer's original console.
original_vt=$(cat /sys/class/tty/tty0/active)
original_vt=${original_vt#tty}
exec </dev/tty5 >/dev/tty5 2>&1
chvt 5
trap 'chvt "$original_vt"' EXIT
clear
printf '\nWelcome to domLight setup\n\nCreate your administrator account to continue.\nThere is no default account or password.\n\n'
while true; do
 read -r -p 'Username (lowercase letters, digits, underscore or hyphen): ' admin_name
 [[ "$admin_name" =~ ^[a-z_][a-z0-9_-]{0,30}$ ]] && [[ "$admin_name" != root ]] && break
 printf 'Choose a valid username other than root.\n'
done
while true; do
 read -r -s -p 'Password (at least 12 characters): ' admin_password; printf '\n'
 read -r -s -p 'Confirm password: ' admin_confirm; printf '\n'
 [[ ${#admin_password} -ge 12 && "$admin_password" == "$admin_confirm" ]] && break
 printf 'Passwords must match and contain at least 12 characters.\n'
done
# Password travels via stdin, never command arguments or installer output.
admin_hash=$(printf '%s\n' "$admin_password" | openssl passwd -6 -stdin)
unset admin_password admin_confirm
[[ "$admin_hash" == '$6$'* ]]
umask 077
printf 'user --name=%s --groups=wheel --iscrypted --password=%s\n' "$admin_name" "$admin_hash" >/tmp/domlight-admin.ks
unset admin_hash
printf '\nAdministrator account configured. Returning to disk selection...\n'
