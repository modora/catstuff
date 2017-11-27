import catstuff.tools.plugins
import random


class Random(catstuff.tools.plugins.StrMethod):
    def shuffle(self):
        l = list(self)
        random.shuffle(l)
        return str(l)
