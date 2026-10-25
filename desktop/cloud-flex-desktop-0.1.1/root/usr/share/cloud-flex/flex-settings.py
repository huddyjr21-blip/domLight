import sys, subprocess
from pathlib import Path
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
import os
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QLineEdit, QScrollArea, QFrame, QSlider

BASE=Path('/usr/share/cloud-flex')
PAGES={
'Network': [('Internet','Connections and wired network','network-wired','kcm_networkmanagement')],
'Personalization': [('Wallpaper','Choose your desktop background','preferences-desktop-wallpaper','kcm_wallpaper'),('Colors and appearance','Window colors and application style','preferences-desktop-theme-global','kcm_colors'),('Fonts','Text size and readability','preferences-desktop-font','kcm_fonts')],
'Device': [('Sound','Output, input and volume','audio-volume-high','kcm_pulseaudio'),('Mouse and touchpad','Pointer speed and scrolling','input-mouse','kcm_mouse'),('Keyboard shortcuts','Keys and shortcut actions','input-keyboard','kcm_keys'),('Night Light','Warmer screen colors in the evening','weather-clear-night','kcm_nightlight'),('Power','Energy use and idle behavior','system-suspend','kcm_powerdevilprofilesconfig')],
'Apps': [('Default apps','Browser and file associations','preferences-desktop-default-applications','kcm_componentchooser'),('Notifications','Manage app notifications','preferences-desktop-notification','kcm_notifications')],
'Accessibility': [('Accessibility','Keyboard, pointer and visual assistance','preferences-desktop-accessibility','kcm_access')],
'System': [('Screen lock','Lock screen and idle locking','system-lock-screen','kcm_screenlocker'),('Language and region','Language, numbers and date formats','preferences-desktop-locale','kcm_regionandlang'),('Desktop session','Sign-in and session behavior','system-log-out','kcm_smserver')]
}
NAVICONS=['network-wired','preferences-desktop-theme-global','computer','applications-all','preferences-desktop-accessibility','preferences-system']


def iconFor(name):
 p=BASE/'flex-icons'/('settings-'+name+'.svg')
 return QIcon(str(p)) if p.exists() else QIcon.fromTheme(name)

class Settings(QWidget):
 def __init__(self):
  super().__init__()
  self.setWindowTitle('Settings')
  self.setWindowIcon(QIcon(str(BASE/'flex-icons/settings-app.svg')))
  self.resize(1060,740)
  self.setMinimumSize(860,600)
  self.category='Device'
  self.modules=subprocess.run(['kcmshell6','--list'],capture_output=True,text=True).stdout
  outer=QHBoxLayout(self); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)
  sidebar=QWidget(); sidebar.setObjectName('sidebar'); sidebar.setFixedWidth(238)
  side=QVBoxLayout(sidebar); side.setContentsMargins(16,26,16,20); side.setSpacing(8)
  brand=QLabel('Settings'); brand.setObjectName('brand'); side.addWidget(brand); side.addSpacing(22)
  self.nav={}
  for (name,rows),icon in zip(PAGES.items(),NAVICONS):
   button=QPushButton(iconFor(icon),name); button.setObjectName('nav'); button.setCheckable(True); button.setMinimumHeight(48); button.setIconSize(QSize(20,20)); button.clicked.connect(lambda checked,n=name:self.select(n)); side.addWidget(button); self.nav[name]=button
  side.addStretch()
  advanced=QPushButton('All system settings'); advanced.setObjectName('secondary'); advanced.clicked.connect(lambda:self.run(['systemsettings'])); side.addWidget(advanced)
  about=QPushButton('About this device'); about.setObjectName('secondary'); about.clicked.connect(lambda:self.select('About')); side.addWidget(about)
  outer.addWidget(sidebar)
  main=QWidget(); column=QVBoxLayout(main); column.setContentsMargins(32,26,32,26); column.setSpacing(24)
  self.search=QLineEdit(); self.search.setPlaceholderText('Search settings'); self.search.setClearButtonEnabled(True); self.search.setMinimumHeight(48); self.search.textChanged.connect(self.render); column.addWidget(self.search)
  self.heading=QLabel(); self.heading.setObjectName('heading'); column.addWidget(self.heading)
  scroll=QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame); scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
  self.content=QWidget(); self.items=QVBoxLayout(self.content); self.items.setContentsMargins(0,0,4,0); self.items.setSpacing(12); scroll.setWidget(self.content); column.addWidget(scroll,1)
  self.message=QLabel(); self.message.setWordWrap(True); self.message.setObjectName('muted'); column.addWidget(self.message)
  outer.addWidget(main,1)
  self.select(self.category)
  self.search.setFocus()
 def run(self,args):
  try:
   subprocess.Popen(args,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True)
   self.message.setText('Opened '+('system settings' if args[0]=='systemsettings' else 'the settings page')+'.')
  except OSError as err:self.message.setText(str(err))
 def select(self,name):
  self.category=name
  self.search.blockSignals(True); self.search.clear(); self.search.blockSignals(False)
  for n,b in self.nav.items():b.setChecked(n==name)
  self.render()
 def render(self):
  while self.items.count():
   item=self.items.takeAt(0)
   if item.widget():item.widget().deleteLater()
  query=self.search.text().strip().lower()
  self.heading.setText('Search results' if query else self.category)
  self.message.clear()
  if self.category=='About' and not query:
   self.about(); self.items.addStretch(); return
  if self.category=='Device' and not query:self.volume()
  rows=[(cat,row) for cat,entries in PAGES.items() for row in entries if (query and query in (' '.join(row[:2])+' '+cat).lower()) or (not query and cat==self.category)]
  count=0
  for cat,(title,subtitle,icon,module) in rows:
   if module not in self.modules:continue
   card=QPushButton(); card.setObjectName('card'); card.setMinimumHeight(84)
   row=QHBoxLayout(card); row.setContentsMargins(22,14,22,14); row.setSpacing(20)
   image=QLabel(); image.setPixmap(iconFor(icon).pixmap(24,24)); image.setFixedWidth(26); row.addWidget(image)
   text=QVBoxLayout(); text.setSpacing(5)
   name=QLabel(title); name.setObjectName('rowtitle'); text.addWidget(name)
   desc=QLabel(subtitle); desc.setObjectName('muted'); desc.setWordWrap(True); text.addWidget(desc); row.addLayout(text,1)
   arrow=QLabel(chr(8250)); arrow.setObjectName('arrow'); row.addWidget(arrow)
   for label in card.findChildren(QLabel):label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
   card.clicked.connect(lambda checked,m=module:self.run(['kcmshell6',m])); self.items.addWidget(card); count+=1
  if not count:self.items.addWidget(QLabel('No settings found. Try another search.'))
  self.items.addStretch()
 def volume(self):
  frame=QFrame(); frame.setObjectName('volumeCard'); box=QVBoxLayout(frame); box.setContentsMargins(22,20,22,20); box.setSpacing(16)
  title=QLabel('Volume'); title.setObjectName('rowtitle'); box.addWidget(title)
  line=QHBoxLayout(); mute=QPushButton(iconFor('audio-volume-high'),''); mute.setToolTip('Mute or unmute'); mute.setObjectName('iconButton'); mute.setFixedSize(40,40); mute.clicked.connect(lambda:self.setMute(mute)); line.addWidget(mute)
  self.slider=QSlider(Qt.Orientation.Horizontal); self.slider.setRange(0,100)
  output=subprocess.run(['pactl','get-sink-volume','@DEFAULT_SINK@'],capture_output=True,text=True).stdout
  import re
  match=re.search(r'([0-9]+)%',output); value=min(100,int(match.group(1))) if match else 100
  self.slider.setValue(value); self.percent=QLabel(str(value)+'%'); self.percent.setFixedWidth(44)
  self.slider.valueChanged.connect(lambda n:self.percent.setText(str(n)+'%')); self.slider.sliderReleased.connect(self.setVolume)
  self.slider.actionTriggered.connect(lambda action:QTimer.singleShot(0,self.setVolume) if action in (1,2,3,4,5,6) else None)
  line.addWidget(self.slider,1); line.addWidget(self.percent); box.addLayout(line); self.items.addWidget(frame)
  self.updateMute(mute)
 def updateMute(self,button):
  muted='yes' in subprocess.run(['pactl','get-sink-mute','@DEFAULT_SINK@'],capture_output=True,text=True).stdout
  button.setIcon(iconFor('audio-volume-muted' if muted else 'audio-volume-high'))
  button.setToolTip('Unmute' if muted else 'Mute')
 def setMute(self,button):
  subprocess.run(['pactl','set-sink-mute','@DEFAULT_SINK@','toggle']); self.updateMute(button)
 def setVolume(self):subprocess.run(['pactl','set-sink-volume','@DEFAULT_SINK@',str(self.slider.value())+'%'])
 def about(self):
  values={}
  for line in Path('/etc/os-release').read_text().splitlines():
   if '=' in line:
    key,value=line.split('=',1); values[key]=value.strip(chr(34))
  frame=QFrame(); frame.setObjectName('volumeCard'); box=QVBoxLayout(frame); box.setContentsMargins(28,28,28,28); box.setSpacing(18)
  title=QLabel('Cloud desktop'); title.setObjectName('heading'); box.addWidget(title)
  description=QLabel('A lightweight desktop for Gmail, Google Drive and the web.'); description.setWordWrap(True); box.addWidget(description)
  osname=QLabel(values.get('PRETTY_NAME','Fedora Linux')); osname.setObjectName('muted'); box.addWidget(osname)
  self.items.addWidget(frame)

app=QApplication(sys.argv)

serverName=str(Path(os.environ.get('XDG_RUNTIME_DIR','/tmp'))/('cloud-flex-settings-'+str(os.getuid())))
client=QLocalSocket(); client.connectToServer(serverName)
if client.waitForConnected(300):
 client.write(b'activate'); client.waitForBytesWritten(300); client.disconnectFromServer(); sys.exit(0)
QLocalServer.removeServer(serverName)
server=QLocalServer(); server.setSocketOptions(QLocalServer.SocketOption.UserAccessOption); server.listen(serverName)

app.setApplicationName('Cloud Settings'); app.setDesktopFileName('cloud-flex-settings'); app.setFont(QFont('Noto Sans',11))
app.setStyle('Fusion')
app.setStyleSheet('''
QWidget { background:#f0f4f9; color:#202124; font-family:"Noto Sans"; font-size:14px; }
QWidget#sidebar { background:#e9eef6; }
QLabel { background:transparent; }
QLabel#brand { font-size:23px; padding-left:16px; }
QLabel#heading { font-size:24px; }
QLabel#rowtitle { font-size:15px; }
QLabel#muted { color:#5f6368; font-size:13px; }
QLabel#arrow { color:#5f6368; font-size:26px; }
QPushButton { border:0; padding:10px; border-radius:22px; }
QPushButton#nav { text-align:left; padding-left:18px; background:transparent; }
QPushButton#nav:checked { background:#c2e7ff; color:#001d35; }
QPushButton#nav:hover,QPushButton#secondary:hover { background:#d3e3fd; }
QPushButton#secondary { text-align:left; color:#444746; background:transparent; font-size:13px; }
QPushButton#card,QFrame#volumeCard { background:white; border-radius:18px; }
QPushButton#card:hover { background:#e1ecfc; }
QPushButton:focus { border:2px solid #0b57d0; }
QLineEdit { background:white; border:1px solid transparent; border-radius:24px; padding:0 22px; font-size:15px; selection-background-color:#c2e7ff; }
QLineEdit:focus { border:1px solid #0b57d0; }
QScrollArea,QScrollArea>QWidget>QWidget { background:transparent; }
QScrollBar:vertical { width:8px; background:transparent; }
QScrollBar::handle:vertical { background:#c4c7c5; border-radius:4px; min-height:36px; }
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical { height:0; }
QSlider::groove:horizontal { height:24px; border-radius:12px; background:#d3e3fd; }
QSlider::sub-page:horizontal { background:#a8c7fa; border-radius:12px; }
QSlider::handle:horizontal { width:4px; background:#0b57d0; margin:-4px 0; border-radius:2px; }
QPushButton#iconButton { background:#e9eef6; border-radius:20px; }
''')
window=Settings(); window.show()
def activateExisting():
 socket=server.nextPendingConnection()
 if window.isMinimized():window.showNormal()
 window.show(); window.raise_(); window.activateWindow()
 socket.disconnectFromServer(); socket.deleteLater()
server.newConnection.connect(activateExisting)
sys.exit(app.exec())
