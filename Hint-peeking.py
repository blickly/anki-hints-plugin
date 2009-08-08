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
from anki.hooks import addHook, wrap
from ankiqt.ui import view
from anki.utils import hexifyID
from ankiqt import mw
import re

# Settings
ANSWER_FIELD="Meaning"
CARD_TEMPLATE="Recognition"
SHOW_HINT_KEY=Qt.Key_R
DEBUG=True

def newKeyPressEvent(evt):
    """Show hint when the SHOW_HINT_KEY is pressed."""
    if mw.state == "showQuestion":
        if (mw.currentCard.cardModel.name == CARD_TEMPLATE
                and evt.key() == SHOW_HINT_KEY):
            evt.accept()
            return mw.moveToState("showHint")
    return oldEventHandler(evt)

def newRedisplay(self):
    """If we are showing the hint, display the answer.
    We will filter away the ANSWER_FIELD with a hook."""
    if self.state == "showHint":
        self.setBackground()
        if not self.main.currentCard.cardModel.questionInAnswer:
            self.drawQuestion(nosound=True)
        if self.drawRule:
            self.write("<hr>")
        self.drawAnswer()
    self.flush()

def filterHint(a, currentCard):
    """If we are showing the hint, filter out the ANSWER_FIELD"""
    if mw.state == "showHint":
        fieldIDs = ["fm" + hexifyID(field.id)
                    for field in currentCard.fact.model.fieldModels
                    if field.name == ANSWER_FIELD]
        for fid in fieldIDs:
            p = re.compile('<span class="%s">.*?</span>' % fid)
            a = p.sub('<span> </span>', a, re.DOTALL)
    return a

addHook("drawAnswer", filterHint)

oldEventHandler = mw.keyPressEvent
mw.keyPressEvent = newKeyPressEvent
view.View.redisplay = wrap(view.View.redisplay, newRedisplay, "after")

mw.registerPlugin("Hint-peeking", 4)
