#-!- coding=utf-8 -!-

#from PySide import QtCore, QtGui
from PyQt4 import QtCore, QtGui
QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

import sys
import time

from widget import NumPadKey, TextEditKey
from interface import Interface


class InputPad( QtGui.QWidget ) :
    KEY_MAP = [ \
            [ "0", [ 4, 1, 1, 1 ], 0.9, ] \
            , \
            [ "1", [ 1, 0, 1, 1 ], 1.0, ] \
            , \
            [ "2", [ 1, 1, 1, 1 ], 1.0, ] \
            , \
            [ "3", [ 1, 2, 1, 1 ], 1.0, ] \
            , \
            [ "4", [ 2, 0, 1, 1 ], 1.0, ] \
            , \
            [ "5", [ 2, 1, 1, 1 ], 1.0, ] \
            , \
            [ "6", [ 2, 2, 1, 1 ], 1.0, ] \
            , \
            [ "7", [ 3, 0, 1, 1 ], 1.0, ] \
            , \
            [ "8", [ 3, 1, 1, 1 ], 1.0, ] \
            , \
            [ "9", [ 3, 2, 1, 1 ], 1.0, ] \
            , \
            [ "undefine", [ 4, 0, 1, 1 ], 0.9, ] \
            , \
            [ "mode", [ 4, 2, 1, 1 ], 0.9, ] \
            , \
            [ "backspace", [ 0, 0, 1, 3 ], 0.85, ] \
            , \
            ]
    KEYCODE_UNDEFINE = 10
    KEYCODE_MODE = 11
    KEYCODE_BACKSPACE = 12
    KEY_HEIGHT = 105
    LAYOUT_SPACING = 0
    MODE_NORMAL = 0
    MODE_SELECT = 1
    MODE_PUNC = 2

    PUNC_MAP = [ \
            [ " ", "\n", "，", "。", "？", "……", "～", "！", ] \
            , \
            [ "、", "；", "：", "“", "”", "——", "（", "）", ] \
            , \
            [ "@", "&", "_", "《", "》", "%", "‘", "’", ] \
            , \
            [ "*", "#", "\\", "+", "-", "=", "*", "/", ] \
            , \
            ]

    FONT_NORMAL = QtGui.QFont()
    FONT_UNDERLINR = QtGui.QFont()
    FONT_UNDERLINR.setUnderline( True )
    def __init__( self, parent = None ) :
        QtGui.QWidget.__init__( self, parent )
        #QtGui.QWidget.__init__( self, parent, QtCore.Qt.Dialog | QtCore.Qt.FramelessWindowHint )
        self.setAttribute( QtCore.Qt.WA_Maemo5PortraitOrientation, True )

        self.layout = QtGui.QVBoxLayout()
        self.layout.setSpacing( self.LAYOUT_SPACING )
        self.setLayout( self.layout )

        self.textedit = TextEditKey( self.KEYCODE_BACKSPACE, self )
        self.textedit.clicked.connect( self.slot_key_click )
        self.textedit.longpressed.connect( self.slot_key_longpress )
        #self.textedit.setReadOnly( True )
        #self.textedit.grabKeyboard()
        self.layout.addWidget( self.textedit )
        
        self.keypad_layout = QtGui.QGridLayout()
        self.keypad_layout.setSpacing( self.LAYOUT_SPACING )
        self.keypad_layout.setContentsMargins( 0, 0, 0, 0 )
        self.layout.addLayout( self.keypad_layout )

        self.key_list = []
        for keycode in range( len( self.KEY_MAP ) ) :
            key_map = self.KEY_MAP[keycode]
            key = NumPadKey( keycode, self )
            key.setFocusProxy( self.textedit )
            key.setText( key_map[0] )
            key.setFixedHeight( self.KEY_HEIGHT * key_map[2] )
            self.keypad_layout.addWidget( key, key_map[1][0], key_map[1][1] ,key_map[1][2] ,key_map[1][3] )
            self.key_list.append( key )
            key.clicked.connect( self.slot_key_click )
            key.longpressed.connect( self.slot_key_longpress )

        #self.key_list[self.KEYCODE_BACKSPACE].enableAutoRepeat()
        self.key_list[self.KEYCODE_BACKSPACE].hide()

        self.interface = Interface()
        self.mode = self.MODE_NORMAL
        self.punc_index = 0

    def update( self ) :
        update_stamp = []
        for i in range( len( self.KEY_MAP ) ) :
            update_stamp.append( False )
        if self.mode == self.MODE_NORMAL :
            index = 1
            for item in self.interface.cand_list :
                #print item
                self.key_list[index].setText( item[2] )
                update_stamp[index] = True
                index = index + 1
            text = self.interface.get_selected() + self.interface.code()
            self.textedit.set_preedit( text )
        elif self.mode == self.MODE_SELECT :
            index = 1
            for item in self.interface.cand_list :
                self.key_list[index].setText( item[2] )
                update_stamp[index] = True
                index = index + 1
            text = self.interface.get_selected() + self.interface.code()
            self.key_list[self.KEYCODE_BACKSPACE].setText( text )
            update_stamp[self.KEYCODE_BACKSPACE] = True
        elif self.mode == self.MODE_PUNC :
            index = 2
            punc_list = self.PUNC_MAP[self.punc_index]
            for punc in punc_list :
                self.key_list[index].setText( punc.decode( "utf-8" ) )
                update_stamp[index] = True
                index = index + 1
        for i in range( len( self.KEY_MAP ) ) :
            if not update_stamp[i] :
                self.key_list[i].setText( self.KEY_MAP[i][0] )

            
    def set_mode( self, mode ) :
        self.mode = mode

        if mode == self.MODE_NORMAL :
            for i in range( 1, 7 ) :
                self.key_list[i].setFont( self. FONT_NORMAL )
        elif mode == self.MODE_SELECT :
            for i in range( 1, 7 ) :
                self.key_list[i].setFont( self. FONT_UNDERLINR )
        elif mode == self.MODE_PUNC :
            self.punc_index = 0
            for i in range( 1, 7 ) :
                self.key_list[i].setFont( self. FONT_NORMAL )
            
    @QtCore.Slot( int )
    def slot_key_click( self, code ) :
        if self.mode == self.MODE_NORMAL :
            if code >= 2 and code <= 9 :
                self.interface.append( str( code ) )
                self.interface.gen_cand_list()
                self.update()
                #for node in self.interface.cand_list :
                    #print node[0], node[1]
            elif code == self.KEYCODE_BACKSPACE :
                if len( self.interface.code() ) > 0 :
                    c = self.interface.pop()
                    self.interface.gen_cand_list()
                    self.update()
                    if len( self.interface.code() ) <= 0 :
                        #self.key_list[code].pause_auto_repeat()
                        #self.key_list[code].disable()
                        pass
                else :
                    cursor = self.textedit.textCursor()
                    cursor.deletePreviousChar()
                    pass
            #elif code == 1 or code == self.KEYCODE_UNDEFINE :
            elif code == 1 :
                if len( self.interface.code() ) > 0 :
                    self.set_mode( self.MODE_SELECT )
                    self.update()
                else :
                    self.set_mode( self.MODE_PUNC )
                    self.update()
        elif self.mode == self.MODE_SELECT :
            if code >= 1 and code <= 6 :
                self.interface.select( code - 1 )
                self.interface.gen_cand_list()
                if len( self.interface.code() ) <= 0 :
                    text = self.interface.get_selected()
                    self.interface.commit()
                    self.textedit.insertPlainText( text )
                    self.set_mode( self.MODE_NORMAL )
                self.update()
            elif code == self.KEYCODE_BACKSPACE :
                c = self.interface.deselect()
                self.interface.gen_cand_list()
                if c == "" :
                    self.set_mode( self.MODE_NORMAL )
                self.update()
            elif code == 7 :
                self.interface.page_prev()
                self.interface.gen_cand_list()
                self.update()
            elif code == 9 :
                self.interface.page_next()
                self.interface.gen_cand_list()
                self.update()
        elif self.mode == self.MODE_PUNC :
            if code >= 2 and code <= 9 :
                index = code - 2
                punc_list = self.PUNC_MAP[self.punc_index]
                self.textedit.insertPlainText( punc_list[index].decode( "utf-8" ) )
                self.set_mode( self.MODE_NORMAL )
                self.update()
            elif code == self.KEYCODE_BACKSPACE :
                self.set_mode( self.MODE_NORMAL )
                self.update()
            #elif code == 1 or code == self.KEYCODE_UNDEFINE :
            elif code == 1 :
                self.punc_index = self.punc_index + 1
                if self.punc_index < len( self.PUNC_MAP ) :
                    pass
                else :
                    self.punc_index = 0
                self.update()
        #self.textedit.setFocus()

    @QtCore.Slot( int )
    def slot_key_longpress( self, code ) :
        if self.mode == self.MODE_NORMAL :
            if code >= 0 and code <= 9 :
                self.textedit.insertPlainText( str( code ) )
        pass

    def closeEvent( self, event ) :
        self.hide()
        #self.interface.backend.save()

if __name__ == "__main__" :
    app = QtGui.QApplication( sys.argv )
    pad = InputPad()
    pad.show()
    sys.exit( app.exec_() )


