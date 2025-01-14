# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ConfirmationDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFrame,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(220, 140)
        Dialog.setMinimumSize(QSize(220, 0))
        Dialog.setMaximumSize(QSize(400, 300))
        self.verticalLayout_2 = QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_main = QFrame(Dialog)
        self.frame_main.setObjectName(u"frame_main")
        self.frame_main.setFrameShape(QFrame.NoFrame)
        self.frame_main.setFrameShadow(QFrame.Plain)
        self.frame_main.setLineWidth(0)
        self.verticalLayout = QVBoxLayout(self.frame_main)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_message = QFrame(self.frame_main)
        self.frame_message.setObjectName(u"frame_message")
        self.frame_message.setMinimumSize(QSize(0, 40))
        self.frame_message.setFrameShape(QFrame.NoFrame)
        self.frame_message.setFrameShadow(QFrame.Plain)
        self.frame_message.setLineWidth(0)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_message)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 11)
        self.label_message = QLabel(self.frame_message)
        self.label_message.setObjectName(u"label_message")
        font = QFont()
        font.setBold(False)
        self.label_message.setFont(font)
        self.label_message.setLineWidth(0)
        self.label_message.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_message)


        self.verticalLayout.addWidget(self.frame_message)

        self.frame_checkbox = QFrame(self.frame_main)
        self.frame_checkbox.setObjectName(u"frame_checkbox")
        self.frame_checkbox.setFrameShape(QFrame.NoFrame)
        self.frame_checkbox.setFrameShadow(QFrame.Plain)
        self.frame_checkbox.setLineWidth(0)
        self.verticalLayout_3 = QVBoxLayout(self.frame_checkbox)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.checkBox_dont_ask_again = QCheckBox(self.frame_checkbox)
        self.checkBox_dont_ask_again.setObjectName(u"checkBox_dont_ask_again")
        self.checkBox_dont_ask_again.setMinimumSize(QSize(0, 25))

        self.verticalLayout_3.addWidget(self.checkBox_dont_ask_again)


        self.verticalLayout.addWidget(self.frame_checkbox)

        self.frame_buttons = QFrame(self.frame_main)
        self.frame_buttons.setObjectName(u"frame_buttons")
        self.frame_buttons.setMaximumSize(QSize(16777215, 30))
        self.frame_buttons.setFrameShape(QFrame.NoFrame)
        self.frame_buttons.setFrameShadow(QFrame.Plain)
        self.frame_buttons.setLineWidth(0)
        self.horizontalLayout = QHBoxLayout(self.frame_buttons)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_cancel_action = QPushButton(self.frame_buttons)
        self.pushButton_cancel_action.setObjectName(u"pushButton_cancel_action")
        self.pushButton_cancel_action.setMinimumSize(QSize(0, 25))
        self.pushButton_cancel_action.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_cancel_action)

        self.pushButton_confirm_action = QPushButton(self.frame_buttons)
        self.pushButton_confirm_action.setObjectName(u"pushButton_confirm_action")
        self.pushButton_confirm_action.setMinimumSize(QSize(0, 25))
        self.pushButton_confirm_action.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout.addWidget(self.pushButton_confirm_action)


        self.verticalLayout.addWidget(self.frame_buttons)


        self.verticalLayout_2.addWidget(self.frame_main)

        QWidget.setTabOrder(self.pushButton_confirm_action, self.pushButton_cancel_action)
        QWidget.setTabOrder(self.pushButton_cancel_action, self.checkBox_dont_ask_again)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_message.setText("")
        self.checkBox_dont_ask_again.setText(QCoreApplication.translate("Dialog", u"Do not ask me again", None))
        self.pushButton_cancel_action.setText(QCoreApplication.translate("Dialog", u"Reject", None))
        self.pushButton_confirm_action.setText(QCoreApplication.translate("Dialog", u"Accept", None))
    # retranslateUi

