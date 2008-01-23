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

from zope.interface import Interface

class IStoredInRDB(Interface):
    """Zope 2 compliant objects stored in RDB only"""

class IRDBFolder(Interface):
    """Zope 2 compliant folder that contains only objects stored in RDB"""

class IKeyIdSubobjectSupport(Interface):
    """Id to Key support"""

    def makeIdFromKey(key):
        """compute a Zope id from a key."""

    def makeKeyFromId(id):
        """compute a RDB key from a Zope id."""

    def isSubobject(id):
        """tells if an id conforms to the given conversion."""

