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

sys.path.append("../common/")
from utils import log_exec, init_log

LOGFILE = "/var/log/hgfiltertools.log"

class Usage(Exception):
    def __init__(self, msg = None, no_error = False):
        Exception.__init__(self, msg, no_error)

class ArgumentCheck(Exception):
    def __init__(self, msg = None, no_error = False):
        Exception.__init__(self, msg, no_error)

class FilterTools:
    """
    Compare srpm between master file and slave file.The tools will generate
    output file.
    """
    def __init__(self, masterFile, slaveFile, appendString,
                 outputFile):
        self.masterFile = masterFile
        self.slaveFile = slaveFile
        self.appendString = appendString
        self.outputFile = outputFile
        self.slaveFileBuffer = None
        self.noChangeList = []
        self.changeList = []

    def _checkEnv(self):
        if not os.path.exists(self.masterFile):
            logging.error("Error: Master file doesn't exist. ")
            return False
        if not os.path.exists(self.slaveFile):
            logging.error("Error: Slave file doesn't exist. ")
            return False
        if os.path.exists(self.outputFile):
            logging.warn("Warn: Output file has existed. ")
        return True

    def _getSlaveFileBuffer(self):
        try:
            with file(self.slaveFile) as f:
                self.slaveFileBuffer = f.read(100000)
        except:
            logging.error("Error: Failed to get slave file buffer.")
            logging.error("Trace back: %s", traceback.format_exc())
        return True

    def _separatePkgFrom(self):
        try:
            with file(self.masterFile) as f:
                logging.debug("The following is srpm from masterFile: ")
                for line in f:
                    logging.debug("========%s========", line.strip())
                    if self.slaveFileBuffer.find(line.strip()):
                        self.noChangeList.append(line)
                    else:
                        self.changeList.append(line)
        except:
            logging.error("Error: filter source rpm ")
            logging.error("Trace back: %s", traceback.format_exc())
        return True

    def execute(self):
        logging.info("Zero: check whether it is append.")
        return True
def parse_options():
    parser = optparse.OptionParser();

    parser.add_option("-a", "--append", dest="appendString", type="string",
                     help="appended string in the tail of each line. adding it for writing wiki")
    parser.add_option("-m", "--master", dest="masterFile", type="string",
                     help="master file which is old srpm list")
    parser.add_option("-s", "--slave", dest="slaveFile", type="string",
                     help="slave file which is the newest srpm list.")
    parser.add_option("-o", "--output", dest="outputFile", type="string",
                     help="output file, default is $PWD/output.out")

    (options, args) = parser.parse_args()

    if not options.appendString:
        options.appendString = ''

    if not options.masterFile:
        raise Usage("Error: Must input master file ")

    if not options.slaveFile:
        raise Usage("Error: Must input slave file ")

    if not options.outputFile:
        options.sourcepath = os.getcwd()+'/filteroutput.out'

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

    ft = FilterTools(options.masterFile, options.slaveFile, options.appendString,
                     options.outputFile)
    if ft.execute():
        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
