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
import logging
import constants

import subprocess
import pexpect
import os
import traceback
import fileinput
import string

def init_log(log_file):
    """
        This function init the logging module.
    """
    FORMAT = '%(asctime)-15s %(message)s'
    try:
        logging.basicConfig(format=FORMAT, filename=log_file, level=logging.DEBUG)
    except:
        logging.basicConfig(format=FORMAT, filename=constants.BAKLOGFILE, filemode='w+', level=logging.DEBUG)
    logging.getLogger('autodoers')

def log_exec(argv):
    """
        This function executes a given shell command while logging it.
    """
    out = None
    err = None
    rc = None
    try:
        logging.debug(argv)
        p = subprocess.Popen(argv , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        rc = p.returncode
        logging.debug(out)
        logging.debug(err)
    except:
        logging.error(traceback.format_exc())
    return (out, err, rc)

def get_rpmbuild_path():
    out = None
    err = None
    ret = None
    out, err, ret = log_exec(['rpm', '--eval', '%{_rpmdir}'])
    if ret != 0 :
        logging.error("it can't get the rpm dir. Error info: %s ." % err )
        return None
    out = string.strip(out, '\n')
    return out

class LoggerUtil:
    """
        add change log (just snapshot SHA-1 hash for ovirt-node and vdsm. )
        for each build and check last SHA-1 hash.
    """
    def __init__(self, vdsm_hashid = "", node_hashid = "", image_name = "", log_dir = ""):
        self.vdsm_hi = vdsm_hashid
        self.node_hi = node_hashid
        self.image_name = image_name
        self.changelog_path = log_dir + "ChangeLog"
        self.file_obj = None

    def recordLog(self):
        """
            Record log for nightlybuild. The log format is :
        imageName:
            ovirt-node:xxxxxx
            vdsm:xxxxxxxx
        """
        try:
            logging.debug("image_name : %s ; vdsm_hi : %s ;node_hi : %s ", self.image_name, self.vdsm_hi, self.node_hi)
            if self.image_name is None or self.node_hi is None or self.vdsm_hi is None:
                logging.error("Failed to check the log value. ")
                return False
            self.file_obj = open(self.changelog_path, 'aw+')
            self.file_obj.write("%s : \n" % self.image_name)
            self.file_obj.write("    vdsm: %s \n" % self.vdsm_hi)
            self.file_obj.write("    ovirt-node: %s \n" % self.node_hi)
            self.file_obj.close()
        except:
            logging.error("Failed to record log. Traceback :")
            logging.error(traceback.format_exc())
            self.file_obj.close()
            return False
        return True

    def isExistID(self, pkg_name, pkg_id, log_dir):
        file_obj = None
        self.changelog_path = log_dir + "ChangeLog"
        try:
            if not os.path.exists(self.changelog_path):
                return False
            file_obj = open(self.changelog_path)
            for line in file_obj.xreadlines():
                if line.find(pkg_name) != -1 and line.find(pkg_id) != -1:
                    return True
        except:
            logging.warn("Failed to find whether the pkg and id exist. ")
            logging.warn(traceback.format_exc())
            return False
        finally:
            if file_obj != None:
                file_obj.close()
        return False
