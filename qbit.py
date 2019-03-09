

import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from qbit.common import *

import qbit.gui.main as Qbit
import qbit.gui.display as Display

import argparse
parser = argparse.ArgumentParser(prog=f"python qbit.py", description=f"{APPLICATION_NAME} {APPLICATION_VERSION} - {APPLICATION_DESCRIPTION}")
parser.add_argument("-s","--settings", help="Edit display settings", action='store_true')
args = parser.parse_args()

if args.settings:
	app = QApplication(sys.argv)

	d = Display.Viewer()
	d.show()

	app.exec_()

def restart_program():
	python = sys.executable
	os.execl(python, python, * sys.argv)

if __name__ == '__main__':

	app = QApplication(sys.argv)

	# Start app here
	GUI = Qbit.Viewer(app,restart_program,"Qbit")
	GUI.show()

	app.exec_()
