
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

import qbit.gui.add_channel as AddChannelDialog

class Viewer(QDialog):

	def clickSSL(self,state):
		if state == Qt.Checked:
			self.DIALOG_CONNECT_VIA_SSL = True
		else:
			self.DIALOG_CONNECT_VIA_SSL = False

	def doConnect(self):

		nick = self.nick.text()
		username = self.username.text()
		realname = self.realname.text()
		host = self.host.text()
		port = self.port.text()
		password = self.password.text()

		#loop
		items = [] 
		for index in range(self.autoChannels.count()): 
			 items.append(self.autoChannels.item(index).text())

		save_autojoin_channels(items)


		errs = []
		if len(nick)==0: errs.append("nickname not entered")
		if len(username)==0: errs.append("username not entered")
		if len(realname)==0: errs.append("real name not entered")
		if len(host)==0: errs.append("host not entered")
		if len(port)==0: errs.append("port not entered")
		if not is_integer(port):
			if port!= "": errs.append(f"invalid port \"{port}\"")
		if len(errs)>0:
			msg = QMessageBox()
			msg.setWindowIcon(QIcon(IMAGE_QBIT_ICON))
			msg.setIcon(QMessageBox.Critical)
			msg.setText("Missing or Invalid Input")
			es = ""
			for e in errs: es = es + f"<li>{e}</li>"
			msg.setInformativeText(f"<ul>{es}</ul>")
			msg.setWindowTitle("Can't connect to IRC")
			msg.exec_()
			return

		port = int(port)

		save_last_server(host,port,password,self.DIALOG_CONNECT_VIA_SSL)

		user = {
			"nick": str(nick),
			"username": str(username),
			"realname": str(realname)
		}
		save_user(user)

		self.parent.connectToIrc(nick,username,realname,host,port,password,self.DIALOG_CONNECT_VIA_SSL,items)


	def __init__(self,parent=None):
		super(Viewer,self).__init__(parent)

		self.parent = parent

		self.DIALOG_CONNECT_VIA_SSL = False

		last_server = get_last_server()

		user = get_user()

		aj = get_autojoins()

		# Server information
		hostLayout = QHBoxLayout()
		self.hostLabel = QLabel("Server")
		self.host = QLineEdit(last_server["host"])
		hostLayout.addWidget(self.hostLabel)
		hostLayout.addStretch()
		hostLayout.addWidget(self.host)

		portLayout = QHBoxLayout()
		self.portLabel = QLabel("Port")
		self.port = QLineEdit(str(last_server["port"]))
		portLayout.addWidget(self.portLabel)
		portLayout.addStretch()
		portLayout.addWidget(self.port)

		passLayout = QHBoxLayout()
		self.passLabel = QLabel(last_server["password"])
		self.password = QLineEdit("")
		passLayout.addWidget(self.passLabel)
		passLayout.addStretch()
		passLayout.addWidget(self.password)

		self.ssl = QCheckBox("Connect via SSL",self)
		self.ssl.stateChanged.connect(self.clickSSL)

		if last_server["ssl"]:
			self.ssl.toggle()

		servLayout = QVBoxLayout()
		servLayout.addLayout(hostLayout)
		servLayout.addLayout(portLayout)
		servLayout.addLayout(passLayout)
		servLayout.addWidget(self.ssl)

		servBox = QGroupBox("IRC Server")
		servBox.setLayout(servLayout)

		# User information
		nickLayout = QHBoxLayout()
		self.nickLabel = QLabel("Nick")
		self.nick = QLineEdit(user["nick"])
		nickLayout.addWidget(self.nickLabel)
		nickLayout.addStretch()
		nickLayout.addWidget(self.nick)

		userLayout = QHBoxLayout()
		self.userLabel = QLabel("Username")
		self.username = QLineEdit(user["username"])
		userLayout.addWidget(self.userLabel)
		userLayout.addStretch()
		userLayout.addWidget(self.username)

		realLayout = QHBoxLayout()
		self.realLabel = QLabel("Real Name")
		self.realname = QLineEdit(user["realname"])
		realLayout.addWidget(self.realLabel)
		realLayout.addStretch()
		realLayout.addWidget(self.realname)

		nurLayout = QVBoxLayout()
		nurLayout.addLayout(nickLayout)
		nurLayout.addLayout(userLayout)
		nurLayout.addLayout(realLayout)

		nickBox = QGroupBox("User Information")
		nickBox.setLayout(nurLayout)

		self.connectButton = QPushButton("Connect")
		self.connectButton.clicked.connect(self.doConnect)

		inputLayout = QVBoxLayout()
		inputLayout.addWidget(nickBox)
		inputLayout.addWidget(servBox)
		inputLayout.addWidget(self.connectButton)

		#############################
		# autojoin channels

		self.autoChannels = QListWidget(self)
		#self.parent.autoChannels.addItem(f"{channel}")
		for c in aj:
			self.autoChannels.addItem(c)

		self.addChannelButton = QPushButton("+")
		self.addChannelButton.clicked.connect(self.doAddChannel)

		self.removeChannelButton = QPushButton("-")
		self.removeChannelButton.clicked.connect(self.doRemoveChannel)

		buttonLayout = QHBoxLayout()
		buttonLayout.addStretch()
		buttonLayout.addWidget(self.addChannelButton)
		buttonLayout.addWidget(self.removeChannelButton)

		autoJoinLayout = QVBoxLayout()
		autoJoinLayout.addWidget(self.autoChannels)
		autoJoinLayout.addLayout(buttonLayout)
		

		chanBox = QGroupBox("Auto-Join Channels")
		chanBox.setLayout(autoJoinLayout)

		#############################

		finalLayout = QHBoxLayout()
		finalLayout.addStretch()
		finalLayout.addLayout(inputLayout)
		finalLayout.addWidget(chanBox)
		finalLayout.addStretch()

		self.setLayout(finalLayout)

	def doAddChannel(self):
		self.x = AddChannelDialog.Viewer(self)
		self.x.show()

	def doRemoveChannel(self):
		self.removeSel()

	def removeSel(self):
	    listItems=self.autoChannels.selectedItems()
	    if not listItems: return        
	    for item in listItems:
	       self.autoChannels.takeItem(self.autoChannels.row(item))



