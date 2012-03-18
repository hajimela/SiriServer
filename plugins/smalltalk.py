#!/usr/bin/python
# -*- coding: utf-8 -*-
#by Joh Gerna

import random
from plugin import *

class smalltalk(Plugin):
    @register("en-US", u"(.*你好.*)")
    def st_hello(self, speech, language):
        if language == 'en-US':
            self.say(u"您好 請問您需要什麼幫助嗎？")
        else:
            self.say("Hello")
        self.complete_request()
