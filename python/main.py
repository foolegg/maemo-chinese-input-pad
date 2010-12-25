#!/usr/bin/python
#-!- coding=utf-8 -!-

from interface import Interface
from inputpad import InputPad

import sys

import dbus
import dbus.service
from dbus.mainloop.qt import DBusQtMainLoop

#from PySide import QtCore, QtGui
from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot

if __name__ == "__main__" :
    app = QtGui.QApplication( sys.argv )
    DBusQtMainLoop( set_as_default=True )

    session_bus = dbus.SessionBus()
    name = dbus.service.BusName( "me.maemo.input.chinese", session_bus )
    pad = InputPad( True )
    iface = Interface( session_bus, pad )
    pad.request_commit.connect( iface.commit )

    print "done"

    sys.exit( app.exec_() )
