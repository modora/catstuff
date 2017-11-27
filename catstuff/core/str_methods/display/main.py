from catstuff.tools.plugins import StrMethod


class Display(StrMethod):
    def mirror(self):
        """ Return a mirror of the string"""
        return self[::-1]