
# Qbit IRC Client
# Copyright (C) 2019  Daniel Hetrick

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore

from qbit.common import *

class Viewer(QDialog):

	def selectBg(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['background'] = color.name()
			self.bgColorText.setText(f"<font color=\"{self.display['background']}\">Background Color</font>")

	def selectT(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['text'] = color.name()
			self.tColorText.setText(f"<font color=\"{self.display['text']}\">Text Color</font>")

	def selectE(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['error'] = color.name()
			self.eColorText.setText(f"<font color=\"{self.display['error']}\">Error Color</font>")

	def selectS(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['system'] = color.name()
			self.sColorText.setText(f"<font color=\"{self.display['system']}\">System Color</font>")

	def selectF(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['self'] = color.name()
			self.fColorText.setText(f"<font color=\"{self.display['self']}\">Client Color</font>")

	def selectU(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['user'] = color.name()
			self.uColorText.setText(f"<font color=\"{self.display['user']}\">User Color</font>")

	def selectA(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['action'] = color.name()
			self.aColorText.setText(f"<font color=\"{self.display['action']}\">Action Color</font>")

	def selectL(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['link'] = color.name()
			self.lColorText.setText(f"<font color=\"{self.display['link']}\">Link Color</font>")

	def selectN(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['notice'] = color.name()
			self.nColorText.setText(f"<font color=\"{self.display['notice']}\">Notice Color</font>")

	def selectM(self):
		color = QColorDialog.getColor()
		if color.isValid():
			self.display['motd'] = color.name()
			self.mColorText.setText(f"<font color=\"{self.display['motd']}\">MOTD Color</font>")

	def getFont(self):
		font, ok = QFontDialog.getFont(QFont(self.display['font'],self.display['fontsize']))
		if ok:
			fname = font.toString()
			fl = fname.split(',')
			fname = fl.pop(0)
			fsize = font.pointSize()
			fbig = fsize + 2
			fsmall = fsize - 2
			self.fontText.setText(f"{fname}")
			self.fontSize.setText(f"{str(fsize)}pt")
			self.display['font'] = fname
			self.display['fontsize'] = fsize
			self.display['fontbig'] = fbig
			self.display['fontsmall'] = fsmall

	def doSave(self):
		self.display['width'] = int(self.winWidth.text())
		self.display['height'] = int(self.winHeight.text())
		save_display_config(self.display)
		#self.close()
		self.restart()

	def clickLinks(self,state):
		if state == Qt.Checked:
			self.display["links"] = True
		else:
			self.display["links"] = False


	def __init__(self,restart_func,parent=None):
		super(Viewer,self).__init__(parent)

		self.restart = restart_func
		self.parent = parent

		self.setWindowTitle(f"{APPLICATION_NAME} Settings")
		self.setWindowIcon(QIcon(IMAGE_QBIT_ICON))

		self.display = loadDisplayConfig()

		bgcolorLayout = QHBoxLayout()
		self.bgColorText = QLabel(f"<font color=\"{self.display['background']}\">Background Color</font>")
		self.bgColor = QPushButton('Select',self)
		self.bgColor.clicked.connect(self.selectBg)
		bgcolorLayout.addWidget(self.bgColorText)
		bgcolorLayout.addStretch()
		bgcolorLayout.addWidget(self.bgColor)

		tcolorLayout = QHBoxLayout()
		self.tColorText = QLabel(f"<font color=\"{self.display['text']}\">Text Color</font>")
		self.tColor = QPushButton('Select',self)
		self.tColor.clicked.connect(self.selectT)
		tcolorLayout.addWidget(self.tColorText)
		tcolorLayout.addStretch()
		tcolorLayout.addWidget(self.tColor)

		ecolorLayout = QHBoxLayout()
		self.eColorText = QLabel(f"<font color=\"{self.display['error']}\">Error Color</font>")
		self.eColor = QPushButton('Select',self)
		self.eColor.clicked.connect(self.selectE)
		ecolorLayout.addWidget(self.eColorText)
		ecolorLayout.addStretch()
		ecolorLayout.addWidget(self.eColor)

		scolorLayout = QHBoxLayout()
		self.sColorText = QLabel(f"<font color=\"{self.display['system']}\">System Color</font>")
		self.sColor = QPushButton('Select',self)
		self.sColor.clicked.connect(self.selectS)
		scolorLayout.addWidget(self.sColorText)
		scolorLayout.addStretch()
		scolorLayout.addWidget(self.sColor)

		fcolorLayout = QHBoxLayout()
		self.fColorText = QLabel(f"<font color=\"{self.display['self']}\">Client Color</font>")
		self.fColor = QPushButton('Select',self)
		self.fColor.clicked.connect(self.selectF)
		fcolorLayout.addWidget(self.fColorText)
		fcolorLayout.addStretch()
		fcolorLayout.addWidget(self.fColor)

		ucolorLayout = QHBoxLayout()
		self.uColorText = QLabel(f"<font color=\"{self.display['user']}\">User Color</font>")
		self.uColor = QPushButton('Select',self)
		self.uColor.clicked.connect(self.selectU)
		ucolorLayout.addWidget(self.uColorText)
		ucolorLayout.addStretch()
		ucolorLayout.addWidget(self.uColor)

		acolorLayout = QHBoxLayout()
		self.aColorText = QLabel(f"<font color=\"{self.display['action']}\">Action Color</font>")
		self.aColor = QPushButton('Select',self)
		self.aColor.clicked.connect(self.selectA)
		acolorLayout.addWidget(self.aColorText)
		acolorLayout.addStretch()
		acolorLayout.addWidget(self.aColor)

		lcolorLayout = QHBoxLayout()
		self.lColorText = QLabel(f"<font color=\"{self.display['link']}\">Link Color</font>")
		self.lColor = QPushButton('Select',self)
		self.lColor.clicked.connect(self.selectL)
		lcolorLayout.addWidget(self.lColorText)
		lcolorLayout.addStretch()
		lcolorLayout.addWidget(self.lColor)

		ncolorLayout = QHBoxLayout()
		self.nColorText = QLabel(f"<font color=\"{self.display['notice']}\">Notice Color</font>")
		self.nColor = QPushButton('Select',self)
		self.nColor.clicked.connect(self.selectN)
		ncolorLayout.addWidget(self.nColorText)
		ncolorLayout.addStretch()
		ncolorLayout.addWidget(self.nColor)

		mcolorLayout = QHBoxLayout()
		self.mColorText = QLabel(f"<font color=\"{self.display['motd']}\">MOTD Color</font>")
		self.mColor = QPushButton('Select',self)
		self.mColor.clicked.connect(self.selectM)
		mcolorLayout.addWidget(self.mColorText)
		mcolorLayout.addStretch()
		mcolorLayout.addWidget(self.mColor)

		colorPicker = QVBoxLayout()
		colorPicker.addLayout(bgcolorLayout)
		colorPicker.addLayout(tcolorLayout)
		colorPicker.addLayout(ecolorLayout)
		colorPicker.addLayout(scolorLayout)
		colorPicker.addLayout(fcolorLayout)

		colorPicker2 = QVBoxLayout()
		colorPicker2.addLayout(ucolorLayout)
		colorPicker2.addLayout(acolorLayout)
		colorPicker2.addLayout(lcolorLayout)
		colorPicker2.addLayout(ncolorLayout)
		colorPicker2.addLayout(mcolorLayout)

		fontLayout = QHBoxLayout()
		self.fontText = QLabel(f"{self.display['font']}")
		self.fontSize = QLabel(f"{self.display['fontsize']}pt")
		self.getFontButton = QPushButton('Select',self)
		self.getFontButton.clicked.connect(self.getFont)
		fontLayout.addWidget(self.fontText)
		fontLayout.addWidget(self.fontSize)
		fontLayout.addStretch()
		fontLayout.addWidget(self.getFontButton)

		fontBox = QGroupBox("Font")
		fontBox.setLayout(fontLayout)

		colorBox = QGroupBox("Colors")
		colorBox.setLayout(colorPicker)

		colorBox2 = QGroupBox("More Colors")
		colorBox2.setLayout(colorPicker2)

		selectColors = QHBoxLayout()
		selectColors.addWidget(colorBox)
		selectColors.addStretch()
		selectColors.addWidget(colorBox2)

		self.dolinks = QCheckBox("Link URLs in chat",self)
		self.dolinks.stateChanged.connect(self.clickLinks)

		if self.display["links"]:
			self.dolinks.toggle()

		widthLayout = QHBoxLayout()
		self.widthLabel = QLabel("Initial window width")
		self.winWidth = QLineEdit(f"{str(self.display['width'])}")
		widthLayout.addWidget(self.widthLabel)
		widthLayout.addStretch()
		widthLayout.addWidget(self.winWidth)

		heightLayout = QHBoxLayout()
		self.heightLabel = QLabel("Initial window height")
		self.winHeight = QLineEdit(f"{str(self.display['height'])}")
		heightLayout.addWidget(self.heightLabel)
		heightLayout.addStretch()
		heightLayout.addWidget(self.winHeight)

		buttonLayout = QHBoxLayout()
		self.save = QPushButton('Save and Restart',self)
		self.save.clicked.connect(self.doSave)
		self.cancel = QPushButton('Exit',self)
		self.cancel.clicked.connect(self.close)
		buttonLayout.addWidget(self.save)
		buttonLayout.addWidget(self.cancel)

		finalLayout = QVBoxLayout()
		finalLayout.addWidget(fontBox)
		finalLayout.addLayout(selectColors)
		finalLayout.addWidget(self.dolinks)
		finalLayout.addLayout(widthLayout)
		finalLayout.addLayout(heightLayout)
		finalLayout.addLayout(buttonLayout)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)

