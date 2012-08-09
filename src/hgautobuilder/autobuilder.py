#!/usr/bin/python
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Refer to the README and COPYING files for full details of the license
#
"""
This tool can check whether the cvs server update, it will
build the bin rpm package if any update exists.
"""

import os
import sys
import logging
import subprocess
import traceback
import shutil

import constants
from utils import init_log , log_exec

class AutoBuilder:
    def __init__(self):
        self.cvstempdir = constants.CVSTEMPDIR
        self.repodir = constants.REPODIR
        self.updatepkg = []
        self.errorpkg = []
        self.binrpm = []

    def _parse_check_result(self, sout):
        try:
            if sout.find(constants.CHECKRESULTKEYNAME) == -1 :
                logging.error("out isn't spec files. failed to check the result.")
                return False

            #find all the pkg name.
            newidx = 0
            oldidx = 0
            while True:
                newidx = sout.find(constants.CHECKRESULTKEYNAME, oldidx, len(sout))
                if newidx == -1:
                    break
                pkgidx = sout.rfind("/", oldidx, newidx)
                logging.debug("newidx : %d  oldidx: %d pkgidx %d " % (newidx, oldidx, pkgidx))
                pkgname = sout[pkgidx+1:newidx]
                logging.debug("pkg name named "+pkgname+ " will be added to updatepkg array.")
                self.updatepkg.append(pkgname)
                oldidx = newidx+len(constants.CHECKRESULTKEYNAME)
        except:
            logging.error("Failed to parse check result...The trace back is :" )
            logging.error(traceback.format_exc())
            return False
        return True

    def _check_update(self):
        # check whether cvs temp dir exists.
        if not os.path.isdir(self.cvstempdir):
            logging.error("Don't exist : " + self.cvstempdir )
            return False

        err = None
        out = None
        ret = None
        logging.info("start check whether the cvs update.")
        # run the cmd to check whether the cvs updates.
        out, err, ret = log_exec([constants.CHECKBINFILE])
        if ret != 0:
            logging.error("Failed to run command cvs.")
            return False

        if self._parse_check_result(out) == False :
            logging.error("Nothing need to update")
            return False

        logging.info("end check process...")
        return True

    def _parse_build_result(self, sout):
         try:
             startkeynameidx = sout.find(constants.BUILDRESULTSTARTKEYNAME)
             endkeynameidx = sout.find(constants.BUILDRESULTENDKEYNAME)

             if startkeynameidx == -1 or endkeynameidx == -1 or sout.find(constants.BUILDRESULTERRORINFO) != -1: 
                 logging.error("The build result is not key word. Maybe it failed to build.")
                 return False

            #find all the pkg name.
             newidx = startkeynameidx
             oldidx = startkeynameidx
             while True:
                 newidx = sout.find(constants.BUILDRPMKEYNAME, oldidx, endkeynameidx)
                 if newidx == -1:
                     break
                 pkgidx = sout.rfind("/", oldidx, newidx)
                 logging.debug("newidx : %d  oldidx: %d pkgidx %d " % (newidx, oldidx, pkgidx))
                 pkgname = sout[pkgidx+1:newidx+len(constants.BUILDRPMKEYNAME)]
                 logging.debug("pkg name named " +pkgname+ " will be added to binrpm array.")
                 self.binrpm.append(pkgname)
                 oldidx = newidx+len(constants.BUILDRPMKEYNAME)+1
         except:
             logging.error("Failed to parse build result...The trace back is :")
             logging.error(traceback.format_exc())
             return True
         return False

    def _update_repo(self):
        if not os.path.isdir(self.repodir):
            logging.error("Don't exist : " + self.repodir )
            return False

        try:
            for rpmname in self.binrpm:
                logging.debug("the pkg ( %s ) will be added to repo ." % (rpmname))
                srcpath = constants.STORAGEDIR+rpmname
                destpath = self.repodir + rpmname
                shutil.copyfile(srcpath, destpath)
        except:
            logging.error("Failed to copy binrpm to repo. traceback is : ")
            logging.error(traceback.format_exc())
            return False

        err = None
        out = None
        ret = None
        out, err, ret = log_exec([constants.CREATEREPOBINFILE, self.repodir])
        if ret != 0:
            logging.error("Failed to run the command createrepo.")
            return False
        return True

    def _build_rpm(self):
        # init the arg
        err = None
        out = None
        ret = None

        # loop to build the package.
        for rpmname in self.updatepkg:
            out, err, ret = log_exec([constants.BUILDBINFILE, '-y -j CTNode' , rpmname])
            if ret != 0:
                self.errorpkg.append(rpmname)
            self._parse_build_result(out)
        #TODO: deal some exception if it exists some package that can't be built.

    def execute(self, isupdaterepo = True):
        #check whether any update exists.
        logging.info("First Step: check update.")
        if self._check_update() == False :
            logging.error("Nothing needs update. So, Exit....")
            sys.exit(1)
        #start build pkg.
        logging.info("Second Step: build pkg.")
        self._build_rpm()
        #update repo
        if not isupdaterepo:
            logging.info("Don't update repo. So..exit...")
            return True

        #create the flag file.
        try:
            if os.path.exists(constants.CREATEIMAGEFLAG):
                pass
            else:
                file(constants.CREATEIMAGEFLAG, 'w').write(str(os.getpid()) + "\n")
                os.chmod(pidfile, 0664)
        except:
            logging.warn("Failed to create file flag. ")

#        logging.info("Third Step: update repo.")
#        if len(self.binrpm) != 0:
#            logging.info("Next step: It will update repo.")
#            if self._update_repo() == False:
#                logging.error("Failed to update repo.Please check it.");
#                sys.exit(2)
#        else:
#            logging.info("Failed to execute the bldpkg. Please check it.")
        return True

def main():
    init_log()
    AutoBuilder().execute()

if __name__ == "__main__":
    sys.exit(main())
