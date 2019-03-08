
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

	def doAdd(self):
		channel = self.name.text()
		key = self.key.text()

		if len(channel)==0:
			self.error_dialog = QErrorMessage()
			self.error_dialog.showMessage("No channel entered!")
			self.close()
			return

		#print(channel,key)
		if key == "":
			self.parent.autoChannels.addItem(f"{channel}")
		else:
			self.parent.autoChannels.addItem(f"{channel}:{key}")
		self.close()

	def __init__(self,parent=None):
		super(Viewer,self).__init__(parent)

		self.parent = parent

		self.setWindowTitle(f"Join channel")

		nameLayout = QHBoxLayout()
		self.nameLabel = QLabel("Channel")
		self.name = QLineEdit()
		nameLayout.addWidget(self.nameLabel)
		nameLayout.addStretch()
		nameLayout.addWidget(self.name)

		keyLayout = QHBoxLayout()
		self.keyLabel = QLabel("Key")
		self.key = QLineEdit()
		#self.key.setEchoMode(QLineEdit.Password)
		keyLayout.addWidget(self.keyLabel)
		keyLayout.addStretch()
		keyLayout.addWidget(self.key)

		# Buttons
		buttons = QDialogButtonBox(self)
		buttons.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
		buttons.accepted.connect(self.doAdd)
		buttons.rejected.connect(self.close)

		finalLayout = QVBoxLayout()
		finalLayout.addLayout(nameLayout)
		finalLayout.addLayout(keyLayout)
		finalLayout.addStretch()
		finalLayout.addWidget(buttons)

		self.setWindowFlags(self.windowFlags()
                    ^ QtCore.Qt.WindowContextHelpButtonHint)

		self.setLayout(finalLayout)
