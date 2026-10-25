#!/usr/bin/python3
"""Apply desktop defaults explicitly, backing up all affected user configuration."""
import argparse,configparser,datetime,json,os,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');p.add_argument('--restore',type=Path);p.add_argument('--home',type=Path,default=Path.home());p.add_argument('--source',type=Path,default=Path('/usr/share/cloud-flex/defaults'));p.add_argument('--offline',action='store_true');a=p.parse_args()
if not a.apply and not a.restore:p.error('Choose --apply or --restore BACKUP_DIRECTORY')
if os.geteuid()==0 and not a.offline:p.error('Run setup as your desktop user, without sudo')
h=a.home.resolve();cfg=h/'.config';cfg.mkdir(parents=True,exist_ok=True)
def shell(action):
 if not a.offline:
  r=subprocess.run(['systemctl','--user',action,'plasma-plasmashell.service'],capture_output=True,text=True)
  if r.returncode:raise RuntimeError(r.stderr or 'Could not manage Plasma shell; use --offline while signed out')
def parser():
 c=configparser.ConfigParser(interpolation=None,delimiters=('=',),strict=False);c.optionxform=str;return c
shell('stop')
try:
 if a.restore:
  manifest=json.loads((a.restore/'manifest.json').read_text())
  for name,existed in manifest.items():
   dest=cfg/name
   if existed:shutil.copy2(a.restore/name,dest)
   elif dest.exists():dest.unlink()
  print('Restored desktop configuration from',a.restore)
 else:
  backup=h/'.local/state/cloud-flex/backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup.mkdir(parents=True)
  manifest={}
  for template in sorted(a.source.iterdir()):
   if not template.is_file():continue
   dest=cfg/template.name;manifest[template.name]=dest.exists()
   if dest.exists():shutil.copy2(dest,backup/template.name)
  (backup/'manifest.json').write_text(json.dumps(manifest,indent=2))
  for template in sorted(a.source.iterdir()):
   if not template.is_file():continue
   dest=cfg/template.name
   if template.name=='plasma-org.kde.plasma.desktop-appletsrc':shutil.copy2(template,dest);continue
   old=parser();old.read(dest);new=parser();new.read(template)
   for section in new.sections():
    if not old.has_section(section):old.add_section(section)
    for key,value in new.items(section):old.set(section,key,value)
   with dest.open('w') as f:old.write(f,space_around_delimiters=False)
  print('Desktop defaults applied. Backup:',backup)
  print('Sign out and select Plasma at login to load all appearance changes.')
finally:shell('start')
