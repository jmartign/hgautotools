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
import os
import optparse
import sys
import logging
import traceback
import shutil

from utils import log_exec, init_log

LOGFILE = "/var/log/hgmakerepo.log"
CREATEREPOBINFILE="/usr/bin/createrepo"

class Usage(Exception):
    def __init__(self, msg = None, no_error = False):
        Exception.__init__(self, msg, no_error)

class RepoCreator:
    """
    choose and copy the packages into its repo, then createrepo.
    """
    def __init__(self, projecttype, projectname, destpath, sourcepath, blackfile, isappend, isignore):
        self.sourcepath = sourcepath
        self.blackfile = blackfile
        self.projecttype = projecttype
        self.projectname = projectname
        self.destpath = destpath
        self.blackrpms = []
        self.isappend = isappend
        self.isignore = isignore

    def _get_blackrpms(self):
        try:
            if self.blackfile is None:
                return True
            with file(self.blackfile) as f:
                logging.debug("The following is black rpms:")
                for line in f:
                    logging.debug("==%s==", line.strip())
                    self.blackrpms.append(line.strip())
        except:
            logging.error("Failed to get blackrpms using blackfile: %s" % self.blackfile)
            logging.error(traceback.format_exc())
            return False
        return True

    def _create_dir(self, dname):
        try:
            if os.path.isdir(dname):
                logging.debug("The path ( %s ) exists. it doesn't need to mkdir." % dname)
                return True
            # the dir exists, but it isn't dir.
            elif os.path.exists(dname):
                logging.error("The path ( %s ) exists. but it isn't dir." % dname)
                return False
            else:
                os.makedirs(dname)
        except:
            logging.error("Failed to create dir (%s) ." % dname)
            logging.error(traceback.format_exc())
            return False
        return True

    def _clean_destdir(self):
        try:
            if os.path.isdir(self.destpath):
                shutil.rmtree(self.destpath)
            if not self._create_dir(self.destpath):
                return False
        except:
            logging.error("Failed to clean destdir (%s) ." % self.destpath)
            logging.error(traceback.format_exc())
            return False
        return True

    def _copy_rpms(self):
        try:
            rpms = os.listdir(self.sourcepath)
            for rpm in rpms:
                if "debuginfo" in rpm:
                    logging.debug("ignore package from checking name : %s. ", rpm)
                    continue
                if self.projecttype == 'product':
                    if rpm in self.blackrpms:
                        logging.debug("ignore package from blacklist: %s", rpm)
                        continue
                sfullrpmpath = self.sourcepath+"/"+rpm
                dfullrpmpath = self.destpath+"/"+rpm
                logging.debug("copy %s into %s .", sfullrpmpath, dfullrpmpath)
                if not os.path.isdir(sfullrpmpath):
                    if os.path.exists(dfullrpmpath):
                        logging.debug("File ( %s ) have existed. so delete it.", dfullrpmpath)
                        os.path.remove(dfullrpmpath)
                    shutil.copy(sfullrpmpath, dfullrpmpath)
                else:
                    if os.path.exists(dfullrpmpath):
                        logging.debug("File ( %s ) have existed. so delete it.", dfullrpmpath)
                        shutil.rmtree(dfullrpmpath)
                    shutil.copytree(sfullrpmpath, dfullrpmpath)
        except:
            logging.error("Failed to copy rpm from sourcepath to destpath. ")
            logging.error(traceback.format_exc())
            return False
        return True

    def _create_repo(self):
        out = None
        err = None
        ret = None
        out, err, ret = log_exec([CREATEREPOBINFILE, self.destpath])
        if ret != 0:
            logging.error("Failed to run the command createrepo.")
            return False
        return True

    def _init_env(self):
        #check and mkdir sourcepath and destpath
        if not self._create_dir(self.sourcepath) or not self._clean_destdir():
            return False
        #get blackrpms.
        if not self._get_blackrpms():
            return False
        return True

    def _update_repo(self):
        if not os.path.exists(self.destpath):
            return False
        if not self._copy_rpms():
            return False
        if not self._create_repo():
            return False
        return True

    def execute(self):
        logging.info("Zero: check whether it is append.")
        if self.isappend:
            if self._update_repo():
                logging.info("Done for update the repo .")
                return True
            else:
                logging.info("Failed for update the repo .")
                return False

        logging.info("Frist: init the env.")
        if not self._init_env():
            return False

        logging.info("Second: copy the rpms into destpath")
        if not self._copy_rpms():
            return False

        if not self.isignore:
            logging.info("Finally: create repo. ")
            if not self._create_repo():
                return False
        else:
            logging.info("ingore to update repo .")

        logging.info("Done for hgmakerepo!!!")
        return True

def parse_options():
    parser = optparse.OptionParser();
    parser.add_option("-t", "--type", dest="projecttype", type="string",
                     help="project type.default is product. Now it only support devel and product.")
    parser.add_option("-p", "--project", dest="projectname", type="string",
                     help="project name.default is CTNode.maybe we should project code name")
    parser.add_option("-d", "--destpath", dest="destpath", type="string",
                     help="repo path. default is /storage/creator/ctnode/yourprojecttype.")
    parser.add_option("-s", "--sourcepath", dest="sourcepath", type="string",
                     help="source path.. default is /vbuild/CTNode/pool/RPMS .")
    parser.add_option("-b", "--blackfile", dest="blackfile", type="string",
                     help="black list file. the file contains the list of rpm full name.")
    parser.add_option("-a", "--append", dest="isappend", default=False, action="store_true",
                     help="adding it means that you only update rpms from your source dir")
    parser.add_option("-i", "--ignore", dest="isignore", default=False, action="store_true",
                     help="ignore that it update repo.")

    (options, args) = parser.parse_args()

    if not options.projecttype:
        options.projecttype = "product"
    else:
        if options.projecttype not in ("devel", "product"):
            raise Usage("Error product type. Only support 'product' and 'devel'")

    if not options.projectname:
        options.projectname = "CTNode"
    else:
        if options.projectname not in ("CTNode"):
            raise Usage("Error product name. Only support 'CTNode' ")

    if not options.destpath:
        options.destpath = "/storage/creator/"+options.projectname+'/'+options.projecttype

    if not options.sourcepath:
        options.sourcepath = "/vbuild/CTNode/pool/RPMS/"

    if options.blackfile:
        if os.path.exists(options.blackfile) and os.path.isfile(options.blackfile):
            pass
        else:
            raise Usage("Error file. Only support regular file.")
    else:
        options.blackfile = None

    return options

def main():
    init_log(LOGFILE)
    try:
        options = parse_options()
    except Usage, (msg, no_error):
        if no_error:
            out = sys.stdout
            ret = 0
        else:
            out = sys.stderr
            ret = 2
        if msg:
            print >> out, msg
        return ret
    logging.info("options : %s", options)

    rc = RepoCreator(options.projecttype, options.projectname, options.destpath, 
                     options.sourcepath, options.blackfile, options.isappend, options.isignore)
    if rc.execute():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
