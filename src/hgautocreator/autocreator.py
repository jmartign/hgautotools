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
This tool can check whether the repo update, it will
build ovirt-image.iso if any update exists.
"""
import os
import shutil
import sys
import logging
import pexpect
import traceback
import constants
from utils import *
from time import strftime
class AutoCreator:
    """
        daily auto buildor for ovirt node.
    """
    def __init__(self):
        self.rpmdir = get_rpmbuild_path()
        self.vdsm_hashid = None
        self.node_hashid = None
        self.timetramp = strftime("%Y%m%d%H%M%S")
        self.is_need_update = False

    def _clean_git_dirs(self):
        pkgs = constants.PROJECT_DICT.keys()
        try:
            for pkg in pkgs:
                if constants.PROJECT_DICT[pkg]['buildFromGit'] == 'yes':
                    pkglocaldir = constants.PROJECT_DICT[pkg]['dir']
                    if os.path.exists(pkglocaldir) :
                        shutil.rmtree(pkglocaldir)
        except:
            logging.error("Failed to clean git dirs.")
            logging.error(traceback.format_exc())
            return False
        return True

    def _clean_flag(self, buildimgflag):
        try:
            os.remove(buildimgflag)
        except:
            logging.error("Can't delete the file %s ." % buildimgflag )
            return False
        return True

    def _git_pull(self, pkgaddress, pkglocaldir, branchname = "ct_product"):
        try:
            logging.debug("Enter _git_pull function.")
            logging.debug("the product is using branch: %s . pkgaddress: %s .", branchname, pkgaddress)
            ret = pexpect.run('%s clone -b %s %s %s' % (constants.GITBINFILE, branchname, pkgaddress, pkglocaldir), events={'password: ':"abc123\n\r"})
            logging.debug("pexpect run ret : %s " % ret)
        except:
            logging.error("Failed to git pull. traceback is : " )
            logging.error(traceback.format_exc())
            return False
        logging.debug("Exit _git_pull function because of success.")
        return True

    def _get_pkg_hashid(self,pkg_localdir):
        out = None
        err = None
        ret = None
        out, err, ret = log_exec([constants.GETLASTIDCMD, pkg_localdir])
        if ret != 0:
            logging.warn("Failed to get pkg hashid. in : %s ", pkg_localdir)
            return None
        out = string.strip(out, '\n')
        return out

    def _build_need_pkg(self, branchname):
        #pull need pkg
        pkgs = constants.PROJECT_DICT.keys()
        try:
            for pkg in pkgs:
                logging.debug("It will git pull pkg %s ." % pkg)
                if constants.PROJECT_DICT[pkg]['buildFromGit'] == 'yes':
                    pkgaddress = constants.PROJECT_DICT[pkg]['url']
                    pkglocaldir = constants.PROJECT_DICT[pkg]['dir']
                    logging.debug("It will invoke git pull using pkgaddress : %s. pkglocaldir : %s" % (pkgaddress, pkglocaldir))
                    if not self._git_pull(pkgaddress, pkglocaldir, branchname):
                        logging.error("It can't download %s . Exiting..." % pkg)
                        return False
                    else:
                        cmd = None
                        if pkg == "ovirt-node":
                            self.node_hashid = self._get_pkg_hashid(pkglocaldir)
                            cmd = constants.BUILDNODERPMCMD
                        elif pkg == "vdsm":
                            self.vdsm_hashid = self._get_pkg_hashid(pkglocaldir)
                            cmd = constants.BUILDVDSMRPMCMD
                        out, err, ret = log_exec([cmd, pkglocaldir])
                        if ret != 0:
                            logging.error("Failed to run cmd : %s " % cmd)
                            return False
        except:
            logging.error("Failed to build need pkg. ")
            logging.error(traceback.format_exc())
            return False

        return True

    def _update_repo(self, updaterepobin, repodir):
        out = None
        err = None
        ret = None
        out, err, ret = log_exec(updaterepobin)
        if ret != 0:
            logging.error("Failed to run the command hgmakeproductrepo.")
            return False
        if not self._copy_buildrpm(repodir):
            return False

        return True

    def _copy_buildrpm(self, repodir):
        #copy pkg into repo
        out = None
        err = None
        ret = None
        try:
            for subdir in ('noarch', 'x86_64'):
                for fd in os.listdir(self.rpmdir+'/'+subdir):
                    if fd.find("ovirt-node") != -1 or fd.find("vdsm") != -1 or fd.find("node_auth") != -1:
                        currentrpmfullpath = self.rpmdir + '/' + subdir+'/'+fd
                        newrpmfullpath = repodir+fd
                        logging.debug("currentrpmfullpath : %s ; newrpmfullpath: %s", currentrpmfullpath, newrpmfullpath)
                        if os.path.exists(newrpmfullpath):
                            logging.debug("%s has exist. So, rm it.", newrpmfullpath)
                            os.remove(newrpmfullpath)
                        shutil.copyfile(currentrpmfullpath, newrpmfullpath)
        except:
            logging.error("Failed to copy File. Traceback")
            logging.error(traceback.format_exc())
            return False

        #createrepo.
        out, err, ret = log_exec([constants.CREATEREPOBINFILE, repodir])
        if ret != 0:
            logging.error("Failed to run the command createrepo.")
            return False
        return True

    def _clean_dir(self):
        try:
            rpmdirpath = None
            for subdir in ('noarch', 'x86_64'):
                rpmdirpath = self.rpmdir + '/' + subdir
                shutil.rmtree(rpmdirpath)
        except:
            logging.error("Failed to rm paths. Traceback:")
            logging.error(traceback.format_exc())
            return False
        return True

    def _init_env(self, imagesdir):
        try:
            if not os.path.exists(imagesdir):
                os.makedirs(imagesdir)
            else:
                if not os.path.isdir(imagesdir):
                    logging.error(" %s exists, but it is not dirs. something it failed. " % imagesdir)
                    return False
                else:
                    return True
            if os.path.exists(constants.OVIRTCACHEDIR):
                logging.info("Delete dir tree : %s", constants.OVIRTCACHEDIR)
                shutil.rmtree(constants.OVIRTCACHEDIR)
        except:
            logging.error("Failed to init env. so exiting...")
            logging.error(traceback.format_exc())
            return False
        return True

    def _create_img(self, imagesdir):
        pkgs = constants.PROJECT_DICT.keys()
        try:
            for pkg in pkgs:
                if pkg == "ovirt-node":
                    pkglocaldir = constants.PROJECT_DICT[pkg]['dir']
                    imgcreatedir = pkglocaldir + '/recipe/'
                    out = None
                    err = None
                    ret = None
                    out, err, ret = log_exec([constants.BUILDIMGCMD, imgcreatedir])
                    #if out.find("Error") != 0:
                    #    logging.error("Failed to create the image. ")
                    #    return False
                    if out.find("fragmd5 =") == -1 :
                        logging.error("Failed to create the image. ")
                        #return False
                    currentimgfullpath = imgcreatedir + "ivnh-image-1.0.0-Alpha.iso"
                    if not self._copy_img_to_storage(currentimgfullpath, imagesdir):
                        return False
        except:
            logging.error("Failed to create image. Traceback:")
            logging.error(traceback.format_exc())
            return False
        return True

    def _copy_img_to_storage(self, fromdir, todir):
        """
            copy the image to storage.
        """
        try:
            newimagename = "ivnh-image-"+self.timetramp+".iso"
            newimagefullpath = todir+newimagename
            logging.debug("it will move from %s to %s", fromdir, newimagefullpath)
            shutil.move(fromdir, newimagefullpath)
            logging.debug("it will record the log in Changelog.")
            if not LoggerUtil(vdsm_hashid = self.vdsm_hashid, node_hashid = self.node_hashid, image_name = newimagename).recordLog():
                return False
        except:
            logging.error("Failed to move img to storage.")
            logging.error(traceback.format_exc())
            return False
        return True

    def _check_update(self, buildimgflag):
        if os.path.exists(buildimgflag) or \
           not LoggerUtil().isExistID("ovirt-node", self.node_hashid) or \
           not LoggerUtil().isExistID("vdsm", self.vdsm_hashid):
            logging.debug("It should create image. because it exists some update.")
            return True
        else:
            logging.debug("It shouldn't create image. because it doesn't exist some update.")
            return False

    def _clean_env(self, buildimgflag):
        if not self._clean_flag(buildimgflag):
            logging.error("Failed to clean flag file.")
        if not self._clean_git_dirs():
            logging.error("Failed to clean git dirs. ")
        return True

    def execute(self):
        products = constants.PRODUCT_DICT.keys()
        for product in products:
            branchname = constants.PRODUCT_DICT[product]['branch']
            repodir = constants.PRODUCT_DICT[product]['repodir']
            imagesdir = constants.PRODUCT_DICT[product]['imagesdir']
            buildimgflag = constants.PRODUCT_DICT[product]['buildimgflag']
            updaterepobin = constants.PRODUCT_DICT[product]['updaterepobin']
            logging.debug("it will create image for product : %s", product)
            if self.execute_unit(branchname, repodir, imagesdir, buildimgflag, updaterepobin):
                logging.error("Failed to create product: %s", product)
        return True

    def execute_unit(self, branchname, repodir, imagesdir, buildimgflag, updaterepobin):
        """
        main process of this class.
        """
        logging.debug("First step: build env.")
        if not self._init_env(imagesdir):
            logging.error("Failed to init env. so Exit...")
            return False

        logging.debug("Second step: it will build need pkg.")
        if not self._build_need_pkg(branchname):
            logging.error("Failed to build needed pkgs.")
            return False

        logging.debug("Third step: it will check whether it needs build image.")
        if not self._check_update(buildimgflag):
            logging.info("No any update exists, exiting...")
            if not self._clean_env(buildimgflag):
                return False
            return True

        logging.debug("Fourth step: It will update repo. ")
        if not self._update_repo(updaterepobin, repodir):
            logging.error("Failed to update repo. ")
            return False

        logging.debug("Fifth step: it will create_img. ")
        if not self._create_img(imagesdir):
            logging.error("Failed to create image. ")
            return False

        logging.debug("Sixth step: clean env...")
        if not self._clean_env(buildimgflag):
            return False

        return True

def main():
    init_log(constants.AUTOCREATORLOGFILE)
    if AutoCreator().execute():
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
