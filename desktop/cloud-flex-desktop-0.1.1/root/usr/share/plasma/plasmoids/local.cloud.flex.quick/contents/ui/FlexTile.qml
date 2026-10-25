import QtQuick
import QtQuick.Controls as QQC2
import org.kde.kirigami as Kirigami
QQC2.Button {
 id:control
 property string symbol:""
 property string subtitle:""
 property bool selected:false
 property bool large:false
 hoverEnabled:true;padding:0
 implicitHeight:large?108:64
 background:Rectangle {radius:control.large?18:28;color:control.down?"#c2d9f5":control.hovered||control.activeFocus?"#d3e3fd":control.selected?"#c2e7ff":control.large?"transparent":"#e9eef6";border.width:control.activeFocus?2:0;border.color:"#0b57d0"}
 contentItem:Item {
  Kirigami.Icon {
   id:picture;source:control.symbol;width:control.large?48:24;height:width
   x:control.large?(parent.width-width)/2:16
   y:control.large?12:(parent.height-height)/2
  }
  Column {
   x:control.large?4:52
   y:control.large?74:(parent.height-height)/2
   width:control.large?parent.width-8:parent.width-68
   spacing:3
   Text {width:parent.width;text:control.text;color:"#202124";font.family:"Noto Sans";font.pixelSize:14;horizontalAlignment:control.large?Text.AlignHCenter:Text.AlignLeft;elide:Text.ElideRight}
   Text {visible:control.subtitle.length>0;width:parent.width;text:control.subtitle;color:"#5f6368";font.pixelSize:12;elide:Text.ElideRight}
  }
 }
}
