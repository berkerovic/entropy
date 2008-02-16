#!/usr/bin/python -tt
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

#    
# Authors:
#    Tim Lauridsen <tla@rasmil.dk>

from entropyConstants import *
from entropyapi import EquoConnection
import types

class PackageWrapper:
    def __init__(self, matched_atom, avail):

        if matched_atom[1] == 0:
            self.dbconn = EquoConnection.clientDbconn
            self.from_installed = True
        else:
            self.dbconn = EquoConnection.openRepositoryDatabase(matched_atom[1])
            self.from_installed = False
        self.matched_atom = matched_atom
        self.available = avail
        self.do_purge = False

    def __str__(self):
        return str(self.dbconn.retrieveAtom(self.matched_atom[0])+"~"+str(self.dbconn.retrieveRevision(self.matched_atom[0])))

    def __cmp__(self, pkg):
        n1 = str(self)
        n2 = str(pkg)
        if n1 > n2:
            return 1
        elif n1 == n2:
            return 0
        else:
            return -1

    def getPkg(self):
        return self.matched_atom

    def getName(self):
        return self.dbconn.retrieveAtom(self.matched_atom[0])

    def getTup(self):
        return (self.getName(),self.getRepoId(),self.dbconn.retrieveVersion(self.matched_atom[0]),self.dbconn.retrieveVersionTag(self.matched_atom[0]),self.dbconn.retrieveRevision(self.matched_atom[0]))

    def versionData(self):
        return (self.dbconn.retrieveVersion(self.matched_atom[0]),self.dbconn.retrieveVersionTag(self.matched_atom[0]),self.dbconn.retrieveRevision(self.matched_atom[0]))

    def getRepoId(self):
        if self.matched_atom[1] == 0:
            return self.dbconn.retrievePackageFromInstalledTable(self.matched_atom[0])
        else:
            return self.matched_atom[1]

    def getIdpackage(self):
        return self.matched_atom[0]

    def getRevision(self):
        return self.dbconn.retrieveRevision(self.matched_atom[0])

    def getSysPkg(self):
        if not self.from_installed:
            return False
        # check if it's a system package
        s = EquoConnection.validatePackageRemoval(self.matched_atom[0])
        return not s

    # 0: from installed db, so it's installed for sure
    # 1: not installed
    # 2: updatable
    # 3: already updated to the latest
    def getInstallStatus(self):
        if self.from_installed:
            return 0
        key, slot = self.dbconn.retrieveKeySlot(self.matched_atom[0])
        matches = EquoConnection.clientDbconn.searchKeySlot(key,slot)
        if not matches:
            return 1
        else:
            rc, matched = EquoConnection.check_package_update(key+":"+slot)
            if rc:
                return 2
            else:
                return 3

    def getVer(self):
        tag = ""
        vtag = self.dbconn.retrieveVersionTag(self.matched_atom[0])
        if vtag:
            tag = "#"+vtag
        tag += "~"+str(self.dbconn.retrieveRevision(self.matched_atom[0]))
        return self.dbconn.retrieveVersion(self.matched_atom[0])+tag

    def getSlot(self):
        return self.dbconn.retrieveSlot(self.matched_atom[0])

    def getKeySlot(self):
        return self.dbconn.retrieveKeySlot(self.matched_atom[0])

    def getDescription(self):
        return self.dbconn.retrieveDescription(self.matched_atom[0])

    def getDownSize(self):
        return self.dbconn.retrieveSize(self.matched_atom[0])

    def getDiskSize(self):
        return self.dbconn.retrieveOnDiskSize(self.matched_atom[0])

    def getIntelligentSize(self):
        if self.from_installed:
            return self.getDiskSizeFmt()
        else:
            return self.getDownSizeFmt()

    def getDownSizeFmt(self):
        return EquoConnection.entropyTools.bytesIntoHuman(self.dbconn.retrieveSize(self.matched_atom[0]))

    def getDiskSizeFmt(self):
        return EquoConnection.entropyTools.bytesIntoHuman(self.dbconn.retrieveOnDiskSize(self.matched_atom[0]))

    def getArch(self):
        return etpConst['currentarch']

    def getEpoch(self):
        return self.dbconn.retrieveDateCreation(self.matched_atom[0])

    def getRel(self):
        return self.dbconn.retrieveBranch(self.matched_atom[0])

    def getAttr(self,attr):
        if attr == "description":
            return self.dbconn.retrieveDescription(self.matched_atom[0])
        elif attr == "category":
            return self.dbconn.retrieveCategory(self.matched_atom[0])
        elif attr == "license":
            return self.dbconn.retrieveLicense(self.matched_atom[0])
        elif attr == "creationdate":
            return self.dbconn.retrieveDateCreation(self.matched_atom[0])
        elif attr == "version":
            return self.dbconn.retrieveVersion(self.matched_atom[0])
        elif attr == "revision":
            return self.dbconn.retrieveRevision(self.matched_atom[0])
        elif attr == "versiontag":
            t = self.dbconn.retrieveVersionTag(self.matched_atom[0])
            if not t: return "None"
            return t
        elif attr == "branch":
            return self.dbconn.retrieveBranch(self.matched_atom[0])
        elif attr == "name":
            return self.dbconn.retrieveName(self.matched_atom[0])
        elif attr == "slot":
            return self.dbconn.retrieveSlot(self.matched_atom[0])

    def _get_time( self ):
        return self.dbconn.retrieveDateCreation(self.matched_atom[0])

    def get_changelog( self ):
        return "No ChangeLog"

    def get_filelist( self ):
        c = list(self.dbconn.retrieveContent(self.matched_atom[0]))
        c.sort()
        return c

    def get_fullname( self ):
        return self.dbconn.retrieveAtom(self.matched_atom[0])

    pkg =  property(fget=getPkg)
    name =  property(fget=getName)
    repoid =  property(fget=getRepoId)
    ver =  property(fget=getVer)
    revision = property(fget=getRevision)
    version = property(fget=getVer)
    release = property(fget=getRel)
    slot = property(fget=getSlot)
    keyslot = property(fget=getKeySlot)
    description =  property(fget=getDescription)
    size =  property(fget=getDownSize)
    intelligentsizeFmt = property(fget=getIntelligentSize)
    sizeFmt =  property(fget=getDownSizeFmt)
    disksize =  property(fget=getDiskSize)
    disksizeFmt =  property(fget=getDiskSizeFmt)
    arch = property(fget=getArch)
    epoch = property(fget=getEpoch)
    pkgtup = property(fget=getTup)
    syspkg = property(fget=getSysPkg)
    install_status = property(fget=getInstallStatus)