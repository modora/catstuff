from catstuff.core import plugins
import random


class Random(plugins.StrMethod):
    def shuffle(self):
        l = list(self)
        random.shuffle(l)
        return ''.join(l)
