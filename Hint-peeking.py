# -*- coding: utf-8 -*-
# Author:  Ben Lickly <blickly at berkeley dot edu>
#         (based on 'Two-step answer' plugin by Eric Pignet)
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
#   Hint-peeking plugin
#
# This plugin allows peeking at some of the fields in a flashcard before
# seeing the answer. This can be used to peek at example sentences,
# pronunciation for Chinese/Japanese/Korean, etc.
#

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from anki.hooks import wrap
from ankiqt.ui import view
from anki.utils import hexifyID
from ankiqt import mw

# Settings
HIDDEN_FIELD_INDEX=1
SHOW_FIELD_KEY=Qt.Key_R
CARD_TEMPLATE="Recognition"


def newKeyPressEvent(evt):
    """Show answer on RET or register answer."""
    if mw.state == "showQuestion" and evt.key() == SHOW_FIELD_KEY:
        if mw.currentCard.cardModel.name == CARD_TEMPLATE:
            evt.accept()
            return mw.moveToState("showHint")
    return oldEventHandler(evt)

def newOnLoadFinished(self):
    self.onLoadFinished()
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

oldEventHandler = mw.keyPressEvent
mw.keyPressEvent = newKeyPressEvent
view.View.redisplay = wrap(view.View.redisplay, newRedisplay, "after")
# We actually would like to use wrap method with pos="after",
# but wrap seems not to work with a method connected to a signal.
# Hence the following hack, with new method calling old one.
view.View.newOnLoadFinished = newOnLoadFinished
mw.connect(mw.mainWin.mainText,
           SIGNAL("loadFinished(bool)"), mw.bodyView.newOnLoadFinished)

mw.registerPlugin("Hint-peeking", 1)
