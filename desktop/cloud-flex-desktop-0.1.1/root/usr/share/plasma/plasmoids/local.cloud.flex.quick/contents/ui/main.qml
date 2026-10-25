import QtQuick
import QtQuick.Window
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as P5
PlasmoidItem {
 id:root
 property bool powerMode:false
 property bool powerBusy:false
 property string powerError:""
 property var state: ({volume:0,audio:false,muted:false,network:"",date:""})
 property string clock:Qt.formatTime(new Date(),"h:mm AP")
 readonly property string helper:"python3 /usr/share/cloud-flex/flex-controls.py "
 function act(action,close){runner.connectSource(helper+action);if(close)root.expanded=false;}
 P5.DataSource {id:runner;engine:"executable";onNewData:(sourceName,data)=>{if(sourceName===root.helper+"status"){try{root.state=JSON.parse(data.stdout);}catch(e){}}if(sourceName.indexOf(root.helper+"do-")===0){root.powerBusy=false;if(data["exit code"]===0){root.expanded=false;}else{root.powerError=data.stdout || data.stderr || "Unable to complete the action.";}}disconnectSource(sourceName);}}
 Timer{interval:5000;running:true;repeat:true;triggeredOnStart:true;onTriggered:{root.clock=Qt.formatTime(new Date(),"h:mm AP");if(root.expanded)root.act("status",false);}}
 onExpandedChanged:if(expanded){powerMode=false;powerBusy=false;powerError="";act("status",false);}
 preferredRepresentation:compactRepresentation
 Plasmoid.icon:"preferences-system"
 Plasmoid.backgroundHints:PlasmaCore.Types.NoBackground
 compactRepresentation:QQC2.Button {
  implicitWidth:156;Layout.minimumWidth:156;Layout.maximumWidth:156;Layout.preferredWidth:156;implicitHeight:44;Accessible.name:"Quick settings"
  background:Rectangle {radius:24;color:parent.hovered || root.expanded?"#d3e3fd":"#e9eef6"}
  contentItem:RowLayout {spacing:8
   Kirigami.Icon {source:"file:///usr/share/cloud-flex/flex-icons/network.svg";Layout.preferredWidth:18;Layout.preferredHeight:18}
   Kirigami.Icon {source:root.state.muted?"audio-volume-muted":"audio-volume-high";Layout.preferredWidth:18;Layout.preferredHeight:18}
   Text{text:root.clock;font.pixelSize:13;color:"#202124"}
  }
  onClicked:root.expanded=!root.expanded
 }
 fullRepresentation:Rectangle {
  id:flexCard
  onVisibleChanged:if(visible)roundCorners.restart()
  Timer {id:roundCorners;interval:80;onTriggered:if(flexCard.Window.window)flexCard.Window.window.borders=15}

  implicitWidth:400;implicitHeight:root.powerMode?420:360;Layout.minimumWidth:400;Layout.maximumWidth:400;Layout.minimumHeight:root.powerMode?420:360;Layout.maximumHeight:root.powerMode?420:360
  color:"#f0f4f9";radius:26
  ColumnLayout {
   visible:!root.powerMode
   anchors.fill:parent;anchors.margins:22;spacing:16
   RowLayout {
    Layout.fillWidth:true
    Text{text:"Quick settings";font.pixelSize:18;font.weight:Font.Medium;color:"#202124"}
    Item{Layout.fillWidth:true}
    QQC2.ToolButton {icon.source:"file:///usr/share/cloud-flex/flex-icons/close.svg";Accessible.name:"Close quick settings";onClicked:root.expanded=false}
   }
   GridLayout {
    columns:2;rowSpacing:10;columnSpacing:10;Layout.fillWidth:true
    FlexTile {Layout.fillWidth:true;text:"Network";subtitle:root.state.network.indexOf("connected")===0?"Connected":"Not connected";symbol:"file:///usr/share/cloud-flex/flex-icons/network.svg";selected:root.state.network.indexOf("connected")===0;onClicked:root.act("network",true)}
    FlexTile {Layout.fillWidth:true;text:"Night Light";symbol:"file:///usr/share/cloud-flex/flex-icons/moon.svg";onClicked:root.act("night",true)}
    FlexTile {Layout.fillWidth:true;text:"Notifications";symbol:"file:///usr/share/cloud-flex/flex-icons/bell.svg";onClicked:root.act("notifications",true)}
    FlexTile {Layout.fillWidth:true;text:"Sound";symbol:"file:///usr/share/cloud-flex/flex-icons/sound.svg";onClicked:root.act("sound",true)}
   }
   Rectangle {
    Layout.fillWidth:true;Layout.preferredHeight:64;color:"#e9eef6";radius:32
    RowLayout {anchors.fill:parent;anchors.margins:10;spacing:6
     QQC2.ToolButton {icon.name:root.state.muted?"audio-volume-muted":"audio-volume-high";enabled:root.state.audio;Accessible.name:"Toggle mute";onClicked:{root.act("mute",false);refresh.restart();}}
     QQC2.Slider {id:volume;
 background:Rectangle {x:volume.leftPadding;y:volume.topPadding+(volume.availableHeight-height)/2;width:volume.availableWidth;height:28;radius:14;color:"#d3e3fd";Rectangle {width:parent.width*volume.visualPosition;height:parent.height;radius:14;color:"#a8c7fa"}}
 handle:Rectangle {x:volume.leftPadding+volume.visualPosition*(volume.availableWidth-width);y:volume.topPadding+(volume.availableHeight-height)/2;width:4;height:32;radius:2;color:"#0b57d0"}
Layout.fillWidth:true;from:0;to:100;stepSize:0;enabled:root.state.audio;value:root.state.volume;Accessible.name:"Volume";onMoved:{if(!pressed){root.act("volume "+Math.round(value),false);refresh.restart();}}onPressedChanged:if(!pressed){root.act("volume "+Math.round(value),false);refresh.restart();}}
     Text{text:root.state.audio?Math.round(volume.value)+"%":"No audio";color:"#444746";font.pixelSize:12;Layout.preferredWidth:40}
    }
   }
   Item{Layout.fillHeight:true}
   RowLayout {
    Layout.fillWidth:true
    Text{text:root.state.date;font.pixelSize:13;color:"#444746"}
    Item{Layout.fillWidth:true}
    QQC2.ToolButton {icon.source:"file:///usr/share/cloud-flex/flex-icons/lock.svg";Accessible.name:"Lock screen";onClicked:root.act("lock",true)}
    QQC2.ToolButton {icon.source:"file:///usr/share/cloud-flex/flex-icons/settings-app.svg";Accessible.name:"Settings";onClicked:root.act("settings",true)}
    QQC2.ToolButton {icon.source:"file:///usr/share/cloud-flex/flex-icons/power.svg";Accessible.name:"Power menu";onClicked:{root.powerMode=true;root.powerError="";}}
   }
  }
  PowerPanel {anchors.fill:parent;anchors.margins:22;visible:root.powerMode;controller:root;onExecute:action=>root.act("do-"+action,false)}
  Timer{id:refresh;interval:350;onTriggered:root.act("status",false)}
  Keys.onEscapePressed:root.expanded=false
 }
}
