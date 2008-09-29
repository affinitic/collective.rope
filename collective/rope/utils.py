# Copyright (c) 2008
# Authors: Project Contributors (see docs/CREDITS.txt)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 or higher
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
from Acquisition import aq_inner


def makeDictionary():
    return {}


def compareDictionary(x, y):
    return x == y


def makeReferenceBag():
    return ReferenceBag()


class ReferenceBag(dict):

    def objectValues(self):
        return self.values()

    def _setObject(self, rID, referenceObject):
        self[rID] = referenceObject

    def _delObject(self, rID):
        del self[rID]


def wrapsetup(ob, parent):
    '''
    Do the necessaries to an object freshly extracted from the database
    '''
    parent = aq_inner(parent)
    # make sure the parent attribute has an aq chain
    # or five.localsitemanager.utils.get_parent becomes confused
    ob.__parent__ = parent
    ob = ob.__of__(parent)
    return ob
