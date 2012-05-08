#!/usr/bin/python

from utils import *
import sys

def main():
    init_log("/root/test")
    #if LoggerUtil(vdsm_hashid = "", node_hashid = "d25a30b3386e9e575b9fb9d801165adbb60cf625", image_name = "ivhn-image-201203222.img").recordLog():
    if not LoggerUtil(vdsm_hashid = "", node_hashid = "", image_name ="").isExistID("node", "d6e27e785082f6b2517aec260f3dbfe99928a34b"):
        print "no exist"
    else:
        print "exist..."
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
