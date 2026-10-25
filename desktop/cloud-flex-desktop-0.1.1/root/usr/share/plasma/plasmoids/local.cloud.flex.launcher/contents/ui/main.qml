import QtQuick
import QtQuick.Window
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.plasma.plasma5support as P5
PlasmoidItem {
 id: root
 property var allApps: []
 property bool showAll: false
 readonly property string helper: "python3 /usr/share/cloud-flex/flex-controls.py "
 readonly property var favoriteIds: ["chromium-browser.desktop","cloud-gmail.desktop","cloud-drive.desktop","cloud-docs.desktop","cloud-files.desktop","cloud-flex-settings.desktop","org.kde.konsole.desktop"]
 function visibleApps(){
  const q=searchText.toLowerCase();
  if(q.length || showAll)return allApps.filter(a=>a.name.toLowerCase().indexOf(q)>=0);
  let result=[];
  for(const id of favoriteIds){const a=allApps.find(x=>x.id===id);if(a)result.push(a);}
  if(!result.some(a=>a.name==='Gmail')){const a=allApps.find(x=>x.name==='Gmail');if(a)result.splice(1,0,a);}
  return result;
 }
 property string searchText: ""
 function launch(key){ runner.connectSource(helper+"launch "+key);root.expanded=false; }
 P5.DataSource {id:runner;engine:"executable";onNewData:(sourceName,data)=>{if(sourceName===root.helper+"apps"){try{root.allApps=JSON.parse(data.stdout);}catch(e){}}disconnectSource(sourceName);}}
 Component.onCompleted:runner.connectSource(helper+"apps")
 onExpandedChanged:if(expanded){searchText="";showAll=false;runner.connectSource(helper+"apps");}
 Plasmoid.icon:"/usr/share/cloud-flex/flex-icons/launcher.svg"
 Plasmoid.backgroundHints:PlasmaCore.Types.NoBackground
 preferredRepresentation:compactRepresentation
 compactRepresentation:QQC2.Button {
  implicitWidth:56;implicitHeight:56
  background:Rectangle{radius:28;color:parent.hovered || root.expanded?"#d3e3fd":"transparent"}
  contentItem:Kirigami.Icon{source:"/usr/share/cloud-flex/flex-icons/launcher.svg";implicitWidth:24;implicitHeight:24}
  onClicked:root.expanded=!root.expanded
  Accessible.name:"Launcher"
 }
 fullRepresentation:Rectangle {
  id:flexCard
  onVisibleChanged:if(visible)roundCorners.restart()
  Timer {id:roundCorners;interval:80;onTriggered:if(flexCard.Window.window)flexCard.Window.window.borders=15}

  implicitWidth:640;implicitHeight:460;Layout.minimumWidth:640;Layout.maximumWidth:640;Layout.minimumHeight:460;Layout.maximumHeight:460
  color:"#f0f4f9";radius:26
  ColumnLayout {
   anchors.fill:parent;anchors.margins:24;spacing:18
   QQC2.TextField {
    id:search;Layout.fillWidth:true;Layout.preferredHeight:52
    placeholderText:"Search your apps";text:root.searchText;leftPadding:22;rightPadding:16
    font.pixelSize:16;color:"#202124";selectByMouse:true
    background:Rectangle {radius:26;color:"#ffffff";border.color:search.activeFocus?"#a8c7fa":"#dce3ed";border.width:1}
    onTextEdited:root.searchText=text
    Keys.onReturnPressed:{const a=root.visibleApps();if(a.length)root.launch(a[0].key);}
    Keys.onEscapePressed:root.expanded=false
    Connections{target:root;function onExpandedChanged(){if(root.expanded)search.forceActiveFocus();}}
   }
   RowLayout {
    Layout.fillWidth:true
    Text{text:root.searchText.length?"Search results":root.showAll?"All apps":"Apps";color:"#444746";font.pixelSize:14}
    Item{Layout.fillWidth:true}
    QQC2.Button {text:root.showAll?"Favorites":"All apps";flat:true;onClicked:root.showAll=!root.showAll}
   }
   QQC2.ScrollView {
    Layout.fillWidth:true;Layout.fillHeight:true;clip:true
    Grid {
     width:parent.width;columns:5;spacing:12
     Repeater {model:root.visibleApps()
      FlexTile {required property var modelData;width:108;height:108;large:true;text:modelData.name;symbol:modelData.icon;onClicked:root.launch(modelData.key)}
     }
    }
   }
   Text {visible:root.visibleApps().length===0;text:"No matching apps";font.pixelSize:14;color:"#5f6368"}
  }
 }
}
