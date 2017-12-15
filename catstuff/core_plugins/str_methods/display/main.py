from catstuff.core.plugins import StrMethod


class Display(StrMethod):
    def reverse(self):
        """ Return a mirror of the string"""
        return self[::-1]