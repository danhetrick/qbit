

import sys
import os

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from qbit.common import *

import qbit.gui.main as Qbit
import qbit.gui.display as Display

def restart_program():
	python = sys.executable
	os.execl(python, python, * sys.argv)

def restart_program_no_arg():
	python = sys.executable
	sys.argv.pop()
	os.execl(python, python, * sys.argv)

import argparse
parser = argparse.ArgumentParser(prog=f"python qbit.py", description=f"{APPLICATION_NAME} {APPLICATION_VERSION} - {APPLICATION_DESCRIPTION}")
parser.add_argument("-s","--settings", help="Edit display settings", action='store_true')
args = parser.parse_args()

if args.settings:
	app = QApplication(sys.argv)

	d = Display.Viewer(restart_program_no_arg)
	d.show()

	app.exec_()

if __name__ == '__main__':

	app = QApplication(sys.argv)

	# Start app here
	GUI = Qbit.Viewer(app,restart_program,"Qbit")
	GUI.show()

	app.exec_()
