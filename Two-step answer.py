# -*- coding: utf-8 -*-

#######################################################
#  Two-step answer plugin
#
# This plugin allows peeking at one of the fields in
# a flashcard before seeing the answer.
#
# Authors: Ben Lickly <blickly at berkeley dot edu>
#          Eric Pignet <eric at erixpage dot com>
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#######################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import wrap
from ankiqt.ui import view
from ankiqt.ui import main
from anki.utils import hexifyID
from ankiqt import mw

# Settings
CARD_MODEL="Recognition"
HIDDEN_FIELD_INDEX=1
SHOW_FIELD_KEY=Qt.Key_R

def newKeyPressEvent(self, evt):
    """Show answer on RET or register answer."""
    if self.state == "showQuestion" and evt.key() == SHOW_FIELD_KEY:
        if self.currentCard.cardModel.name == CARD_MODEL:
            evt.accept()
            return self.moveToState("showHint")

def newOnLoadFinished(self):
    #self.onLoadFinished()
    if self.state == "showHint":
        mf = self.body.page().mainFrame()
        modelID = "cma" + hexifyID(self.main.currentCard.cardModel.id)
        # FIXME: Using a fixed field index is not a general solution.
        mf.evaluateJavaScript("document.getElementById('" + modelID + "')"
                + ".childNodes["+str(HIDDEN_FIELD_INDEX*2)+"]"
                + ".style.visibility='hidden'")

def newRedisplay(self):
    if self.state == "showHint":
        self.setBackground()
        if not self.main.currentCard.cardModel.questionInAnswer:
            self.drawQuestion(nosound=True)
        if self.drawRule:
            self.write("<hr>")
        self.drawAnswer()
        self.flush()

# We actually would like to use wrap method with pos="after", but wrap seems not to work with a method connected to a signal.
# Hence the following hack, with new method calling old one.
view.View.newOnLoadFinished = newOnLoadFinished
mw.connect(mw.mainWin.mainText, SIGNAL("loadFinished(bool)"), mw.bodyView.newOnLoadFinished)

view.View.redisplay = wrap(view.View.redisplay, newRedisplay, "after")

main.AnkiQt.keyPressEvent = wrap(main.AnkiQt.keyPressEvent, newKeyPressEvent, "before")

