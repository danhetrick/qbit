

import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from qbit.common import *

import qbit.gui.main as Qbit

def restart_program():
	python = sys.executable
	os.execl(python, python, * sys.argv)

if __name__ == '__main__':

	app = QApplication(sys.argv)

	# Start app here
	GUI = Qbit.Viewer(app,restart_program,"Qbit")
	GUI.show()

	app.exec_()
