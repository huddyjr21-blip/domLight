from pathlib import Path
import subprocess,sys,json,configparser,hashlib,re,os
h=Path.home()
def call(a):
 return subprocess.run(a,capture_output=True,text=True,timeout=4).stdout.strip()
def start(a):
 subprocess.Popen(a,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
def apps():
 found={}
 for base in [h/'.local/share/applications',Path('/usr/local/share/applications'),Path('/usr/share/applications')]:
  if not base.exists():continue
  for p in base.glob('*.desktop'):
   if p.name in found:continue
   found[p.name]=p
 out=[]
 for name,p in found.items():
  try:
   c=configparser.ConfigParser(interpolation=None,strict=False);c.read(p);d=c['Desktop Entry']
   if d.get('Type')!='Application' or d.get('NoDisplay','false')=='true' or d.get('Hidden','false')=='true':continue
   if d.get('OnlyShowIn') and 'KDE' not in d.get('OnlyShowIn'):continue
   if 'KDE' in d.get('NotShowIn',''):continue
   if not d.get('Exec'):continue
   title=d.get('Name',name)
   if name=='nemo.desktop':title='Files'
   if name=='chromium-browser.desktop':title='Chromium'
   out.append(dict(key=hashlib.sha256(name.encode()).hexdigest()[:16],name=title,icon=d.get('Icon','application-x-executable'),file=str(p),id=name))
  except Exception:pass
 return sorted(out,key=lambda x:x['name'].lower())
a=sys.argv[1] if len(sys.argv)>1 else 'status'
if a.startswith('do-'):
 commands={'shutdown':['qdbus-qt6','org.kde.Shutdown','/Shutdown','org.kde.Shutdown.logoutAndShutdown'],'restart':['qdbus-qt6','org.kde.Shutdown','/Shutdown','org.kde.Shutdown.logoutAndReboot'],'logout':['qdbus-qt6','org.kde.Shutdown','/Shutdown','org.kde.Shutdown.logout'],'sleep':['systemctl','suspend']}
 command=commands.get(a[3:])
 if command is None:raise SystemExit(2)
 if '--dry-run' in sys.argv:print(json.dumps(command));raise SystemExit()
 r=subprocess.run(command,capture_output=True,text=True)
 if r.returncode:print(r.stderr.strip() or 'The session could not complete this action.')
 raise SystemExit(r.returncode)
if a=='apps':print(json.dumps(apps()))
elif a=='launch':
 for x in apps():
  if x['key']==sys.argv[2]:start(['gio','launch',x['file']]);break
elif a=='status':
 v=call(['pactl','get-sink-volume','@DEFAULT_SINK@']);m=re.search(r'([0-9]+)%',v)
 print(json.dumps(dict(volume=int(m.group(1)) if m else 0,audio=bool(m),muted='yes' in call(['pactl','get-sink-mute','@DEFAULT_SINK@']),network=call(['nmcli','-t','-f','STATE','general']),date=call(['date','+%a, %b %-d']))))
elif a=='volume':subprocess.run(['pactl','set-sink-volume','@DEFAULT_SINK@',str(max(0,min(100,int(sys.argv[2]))))+'%'])
elif a=='mute':subprocess.run(['pactl','set-sink-mute','@DEFAULT_SINK@','toggle'])
elif a in ['network','sound','notifications','night']:
 start(['kcmshell6',dict(network='kcm_networkmanagement',sound='kcm_pulseaudio',notifications='kcm_notifications',night='kcm_nightlight')[a]])
elif a=='settings':start(['python3',str(Path.home()/'.local/share/cloud-desktop/flex-settings.py')])
elif a=='lock':start(['loginctl','lock-session'])
elif a=='power':start(['qdbus-qt6','org.kde.LogoutPrompt','/LogoutPrompt','org.kde.LogoutPrompt.promptAll'])
elif a=='logout':start(['qdbus-qt6','org.kde.LogoutPrompt','/LogoutPrompt','org.kde.LogoutPrompt.promptLogout'])
