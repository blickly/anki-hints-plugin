# -*- coding: utf-8 -*-
# Author:  Ben Lickly <blickly at berkeley dot edu>
#         (inspired by the 'Two-step answer' plugin by Eric Pignet)
# License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
#
#   Hint-peeking plugin
#
# This plugin allows peeking at some of the fields in a flashcard before
# seeing the answer. This can be used to peek at example sentences,
# pronunciation for Chinese/Japanese/Korean, etc.

########################### Settings #######################################
# The following settings can be changed to suit your needs. Lines
# starting with a pound sign (#) are comments and are ignored.

# SHOW_HINT_KEY defines the key that will reveal the hint fields.
SHOW_HINT_KEY=u"r"

# ANSWER_FIELDS defines a list of fields that should _not_ be revealed
# when the show hint key is pressed.
ANSWER_FIELDS=["Meaning"]

# CARD_TEMPLATES defines a list of card templates for which hints may
# be used. Other templates will not show anything when the show hint key
# is pressed.
CARD_TEMPLATES=["Recognition"]
######################### End of Settings ##################################

import re
from anki.hooks import addHook, wrap
from anki.utils import hexifyID
from ankiqt.ui.main import AnkiQt
from ankiqt.ui.view import View
from ankiqt import mw

def newKeyPressEvent(self, evt, _old):
    """Show hint when the SHOW_HINT_KEY is pressed."""
    if self.state == "showQuestion":
        if (self.currentCard.cardModel.name in CARD_TEMPLATES
                and unicode(evt.text()) == SHOW_HINT_KEY):
            evt.accept()
            return self.moveToState("showHint")
    return _old(self, evt)

def newRedisplay(self):
    """If we are showing the hint, display the answer.
    We will filter away the ANSWER_FIELDS with a hook."""
    if self.state == "showHint":
        self.setBackground()
        if not self.main.currentCard.cardModel.questionInAnswer:
            self.drawQuestion(nosound=True)
        if self.drawRule:
            self.write("<hr>")
        self.drawAnswer()
        self.flush()

def filterHint(a, currentCard):
    """If we are showing the hint, filter out the ANSWER_FIELDS"""
    if mw.state == "showHint":
        fieldIDs = ["fm" + hexifyID(field.id)
                    for field in currentCard.fact.model.fieldModels
                    if field.name in ANSWER_FIELDS]
        for fid in fieldIDs:
            p = re.compile('<span class="%s">.*?</span>' % fid)
            a = p.sub('<span> </span>', a, re.DOTALL | re.IGNORECASE)
    return a

addHook("drawAnswer", filterHint)
AnkiQt.keyPressEvent = wrap(AnkiQt.keyPressEvent, newKeyPressEvent, "around")
View.redisplay = wrap(View.redisplay, newRedisplay, "after")

mw.registerPlugin("Hint-peeking", 7)
