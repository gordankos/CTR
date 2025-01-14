# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SaveBeforeCloseDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(450, 150)
        Dialog.setMinimumSize(QSize(450, 150))
        Dialog.setMaximumSize(QSize(450, 150))
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
        self.frame_save_info = QFrame(self.frame_main)
        self.frame_save_info.setObjectName(u"frame_save_info")
        self.frame_save_info.setMinimumSize(QSize(0, 40))
        self.frame_save_info.setFrameShape(QFrame.NoFrame)
        self.frame_save_info.setFrameShadow(QFrame.Plain)
        self.frame_save_info.setLineWidth(0)
        self.verticalLayout_3 = QVBoxLayout(self.frame_save_info)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_title = QLabel(self.frame_save_info)
        self.label_title.setObjectName(u"label_title")

        self.verticalLayout_3.addWidget(self.label_title)

        self.label_filepath = QLabel(self.frame_save_info)
        self.label_filepath.setObjectName(u"label_filepath")

        self.verticalLayout_3.addWidget(self.label_filepath, 0, Qt.AlignBottom)

        self.frame_filepath = QFrame(self.frame_save_info)
        self.frame_filepath.setObjectName(u"frame_filepath")
        self.frame_filepath.setFrameShape(QFrame.NoFrame)
        self.frame_filepath.setFrameShadow(QFrame.Sunken)
        self.frame_filepath.setLineWidth(0)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_filepath)
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.lineEdit_filepath = QLineEdit(self.frame_filepath)
        self.lineEdit_filepath.setObjectName(u"lineEdit_filepath")
        self.lineEdit_filepath.setMinimumSize(QSize(0, 30))
        self.lineEdit_filepath.setMaximumSize(QSize(16777215, 30))

        self.horizontalLayout_2.addWidget(self.lineEdit_filepath)

        self.pushButton_directory_browser = QPushButton(self.frame_filepath)
        self.pushButton_directory_browser.setObjectName(u"pushButton_directory_browser")
        self.pushButton_directory_browser.setMinimumSize(QSize(30, 30))
        self.pushButton_directory_browser.setMaximumSize(QSize(30, 30))
        self.pushButton_directory_browser.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_2.addWidget(self.pushButton_directory_browser)


        self.verticalLayout_3.addWidget(self.frame_filepath)


        self.verticalLayout.addWidget(self.frame_save_info)

        self.frame_buttons = QFrame(self.frame_main)
        self.frame_buttons.setObjectName(u"frame_buttons")
        self.frame_buttons.setMaximumSize(QSize(16777215, 30))
        self.frame_buttons.setFrameShape(QFrame.NoFrame)
        self.frame_buttons.setFrameShadow(QFrame.Plain)
        self.frame_buttons.setLineWidth(0)
        self.horizontalLayout = QHBoxLayout(self.frame_buttons)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_save = QPushButton(self.frame_buttons)
        self.pushButton_save.setObjectName(u"pushButton_save")
        self.pushButton_save.setMinimumSize(QSize(70, 25))
        self.pushButton_save.setMaximumSize(QSize(70, 25))

        self.horizontalLayout.addWidget(self.pushButton_save)

        self.pushButton_dont_save = QPushButton(self.frame_buttons)
        self.pushButton_dont_save.setObjectName(u"pushButton_dont_save")
        self.pushButton_dont_save.setMinimumSize(QSize(90, 25))
        self.pushButton_dont_save.setMaximumSize(QSize(90, 25))

        self.horizontalLayout.addWidget(self.pushButton_dont_save)

        self.pushButton_cancel = QPushButton(self.frame_buttons)
        self.pushButton_cancel.setObjectName(u"pushButton_cancel")
        self.pushButton_cancel.setMinimumSize(QSize(70, 25))
        self.pushButton_cancel.setMaximumSize(QSize(70, 25))

        self.horizontalLayout.addWidget(self.pushButton_cancel)


        self.verticalLayout.addWidget(self.frame_buttons, 0, Qt.AlignRight)


        self.verticalLayout_2.addWidget(self.frame_main)

        QWidget.setTabOrder(self.lineEdit_filepath, self.pushButton_save)
        QWidget.setTabOrder(self.pushButton_save, self.pushButton_dont_save)
        QWidget.setTabOrder(self.pushButton_dont_save, self.pushButton_cancel)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_title.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Save changes to the current file?</span></p></body></html>", None))
        self.label_filepath.setText(QCoreApplication.translate("Dialog", u"Filepath", None))
        self.pushButton_directory_browser.setText("")
        self.pushButton_save.setText(QCoreApplication.translate("Dialog", u"Save", None))
        self.pushButton_dont_save.setText(QCoreApplication.translate("Dialog", u"Don't Save", None))
        self.pushButton_cancel.setText(QCoreApplication.translate("Dialog", u"Cancel", None))
    # retranslateUi

