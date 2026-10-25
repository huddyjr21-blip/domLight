import QtQuick
import QtQuick.Controls as QQC2
import QtQuick.Layouts
import org.kde.kirigami as Kirigami
Item {
 id: panel
 required property var controller
 property string pending: ""
 readonly property var labels: ({shutdown:"Shut down",restart:"Restart",sleep:"Sleep",logout:"Sign out"})
 readonly property var symbols: ({shutdown:"power",restart:"restart",sleep:"moon",logout:"logout"})
 signal execute(string action)
 function choose(action){pending=action;controller.powerError="";}
 Connections {target:controller;function onExpandedChanged(){if(!controller.expanded){panel.pending="";controller.powerBusy=false;controller.powerError="";}}}
 ColumnLayout {
  anchors.fill:parent;spacing:12
  RowLayout {
   Layout.fillWidth:true
   QQC2.ToolButton {icon.source:"file:///usr/share/cloud-flex/flex-icons/back.svg";Accessible.name:"Back";enabled:!controller.powerBusy;onClicked:{if(panel.pending.length)panel.pending="";else controller.powerMode=false;}}
   Text {text:panel.pending.length?panel.labels[panel.pending]+"?":"Power";font.pixelSize:20;font.weight:Font.Medium;color:"#202124"}
   Item {Layout.fillWidth:true}
   QQC2.ToolButton {icon.source:"file:///usr/share/cloud-flex/flex-icons/close.svg";Accessible.name:"Close power menu";enabled:!controller.powerBusy;onClicked:controller.expanded=false}
  }
  GridLayout {
   visible:!panel.pending.length;columns:1;rowSpacing:8;columnSpacing:0;Layout.fillWidth:true
   Repeater {
    model:["shutdown","restart","sleep","logout"]
    FlexTile {required property string modelData;Layout.fillWidth:true;Layout.preferredHeight:52;text:panel.labels[modelData];symbol:"file:///usr/share/cloud-flex/flex-icons/"+panel.symbols[modelData]+".svg";onClicked:panel.choose(modelData)}
   }
  }
  Text {
   visible:!panel.pending.length;Layout.fillWidth:true;wrapMode:Text.WordWrap
   text:"Choose what to do with this virtual machine.";font.pixelSize:14;color:"#5f6368"
  }
  Rectangle {
   visible:panel.pending.length>0;Layout.alignment:Qt.AlignHCenter;Layout.preferredWidth:76;Layout.preferredHeight:76;radius:38;color:"#d3e3fd"
   Kirigami.Icon {anchors.centerIn:parent;width:32;height:32;source:panel.pending.length?"file:///usr/share/cloud-flex/flex-icons/"+panel.symbols[panel.pending]+".svg":""}
  }
  Text {
   visible:panel.pending.length>0;Layout.fillWidth:true;wrapMode:Text.WordWrap;horizontalAlignment:Text.AlignHCenter
   text:panel.pending==="sleep"?"Put the virtual machine to sleep and keep your apps open.":panel.pending==="logout"?"Close your apps and return to the sign-in screen. Save your work first.":panel.pending==="restart"?"Close your apps and restart the virtual machine. Save your work first.":"Close your apps and shut down the virtual machine. Save your work first."
   font.pixelSize:15;color:"#444746"
  }
  Text {visible:controller.powerError.length>0;Layout.fillWidth:true;wrapMode:Text.WordWrap;text:controller.powerError;color:"#b3261e";font.pixelSize:13}
  Item {Layout.fillHeight:true}
  RowLayout {
   visible:panel.pending.length>0;Layout.fillWidth:true;spacing:12
   QQC2.Button {
    id:cancel;Layout.fillWidth:true;Layout.preferredHeight:44;text:"Cancel";enabled:!controller.powerBusy
    contentItem:Text{text:cancel.text;color:"#202124";font.pixelSize:14;horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter}
    background:Rectangle{radius:22;color:cancel.hovered?"#d3e3fd":"#e9eef6";border.color:cancel.activeFocus?"#0b57d0":"transparent";border.width:2}
    onClicked:panel.pending=""
   }
   QQC2.Button {
    id:confirm;Layout.fillWidth:true;Layout.preferredHeight:44;text:controller.powerBusy?"Working...":panel.labels[panel.pending] || "Continue";enabled:!controller.powerBusy
    contentItem:Text{text:confirm.text;color:"#202124";font.pixelSize:14;horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter}
    background:Rectangle{radius:22;color:confirm.hovered?"#b8d7fa":"#c2e7ff";border.color:confirm.activeFocus?"#0b57d0":"transparent";border.width:2}
    onClicked:{controller.powerBusy=true;panel.execute(panel.pending);}
   }
  }
  QQC2.Button {
   id:back;visible:!panel.pending.length;Layout.fillWidth:true;Layout.preferredHeight:44;text:"Back to Quick settings"
   contentItem:Text{text:back.text;color:"#202124";font.pixelSize:14;horizontalAlignment:Text.AlignHCenter;verticalAlignment:Text.AlignVCenter}
    background:Rectangle{radius:22;color:back.hovered?"#d3e3fd":"#e9eef6";border.width:back.activeFocus?2:0;border.color:"#0b57d0"}
   onClicked:controller.powerMode=false
  }
 }
 Keys.onEscapePressed:{if(panel.pending.length)panel.pending="";else controller.powerMode=false;}
}
