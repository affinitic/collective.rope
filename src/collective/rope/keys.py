import re


class KeyIdSubobjectSupport(object):

    def __init__(self, context):
        self.context = context

    def makeIdFromKey(self, key):
        """see interfaces"""
        return str(key)

    def makeKeyFromId(self, id):
        """see interfaces"""
        return int(id)

    def isSubobject(self, id):
        """see interfaces"""
        if id is None:
            return False
        try:
            id = unicode(id)
        except:
            return False

        def isInt(id):
            m = re.compile(r'^([+-])?\d+$')
            return bool(m.match(id))
        return isInt(id)
