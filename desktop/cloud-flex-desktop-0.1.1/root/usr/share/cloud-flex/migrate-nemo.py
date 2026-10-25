#!/usr/bin/python3
from pathlib import Path
import configparser,datetime,shutil,subprocess
h=Path.home();state=h/'.local/state/cloud-flex';stamp=state/'nemo-0.1.1'
if stamp.exists():raise SystemExit()
cfg=h/'.config';cfg.mkdir(exist_ok=True,parents=True)
bak=state/'backups'/('nemo-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));bak.mkdir(parents=True)
for name in ['plasma-org.kde.plasma.desktop-appletsrc','mimeapps.list','gtk-3.0/settings.ini']:
 p=cfg/name
 if p.exists():
  dst=bak/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
p=cfg/'plasma-org.kde.plasma.desktop-appletsrc'
if p.exists():p.write_text(p.read_text().replace('org.kde.dolphin.desktop','nemo.desktop'))
for name,section,key,value in [('mimeapps.list','Default Applications','inode/directory','cloud-files.desktop;'),('gtk-3.0/settings.ini','Settings','gtk-theme-name','CloudFlexNemo')]:
 p=cfg/name;p.parent.mkdir(parents=True,exist_ok=True);c=configparser.ConfigParser(interpolation=None,delimiters=('=',),strict=False);c.optionxform=str;c.read(p)
 if not c.has_section(section):c.add_section(section)
 c.set(section,key,value)
 with p.open('w') as f:c.write(f,space_around_delimiters=False)
for key,value in [('show-desktop-icons','false'),('show-computer-icon','false')]:
 subprocess.run(['gsettings','set','org.nemo.desktop',key,value],capture_output=True)
stamp.write_text(str(bak)+'\n')
