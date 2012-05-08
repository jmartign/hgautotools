#! /usr/bin/python

AUTOBUILDERLOGFILE = '/var/log/autobuilder.log'
AUTOCREATORLOGFILE = '/var/log/autocreator.log'

BAKLOGFILE = '/dev/stdout'

# for autobuilder
CVSTEMPDIR = '/home/autobuild/workspace/'
# REPODIR = '/storage/repo/'
REPODIR = '/storage/creator/CTNode/product/'
STORAGEDIR = '/vbuild/CTNode/pool/RPMS/'
CHECKRESULTKEYNAME = '.spec'

BUILDRESULTSTARTKEYNAME = 'CREATED RPM'
BUILDRESULTENDKEYNAME = 'Checking confliction with other packages directories'
BUILDRESULTERRORINFO = '** Error **'
BUILDRPMKEYNAME = '.rpm'

EXPECTPASSWORD = 'password:'
GITPASSWORD = 'abc123\n\r'
CHECKBINFILE = './hgcvsupdate'
BUILDBINFILE = '/usr/bin/bldpkg'
CREATEREPOBINFILE = '/usr/bin/createrepo'
GITBINFILE = '/usr/bin/git'

CREATEIMAGEFLAG = '/var/run/buildimg.flag'
IMAGESTORAGE = '/storage/BACKUP/ISO/ovirt/nightlybuild/'
#IMAGESTORAGE = '/root/'



BUILDNODERPMCMD = '/usr/share/autocreator/hgbuildnoderpm'
BUILDVDSMRPMCMD = '/usr/share/autocreator/hgbuildvdsmrpm'
BUILDIMGCMD = '/usr/share/autocreator/hgbuildimg'
GETLASTIDCMD = '/usr/share/autocreator/hggetlastlog'

#BUILDNODERPMCMD = '/usr/share/autodoers/hgbuildnoderpm'
#BUILDVDSMRPMCMD = '/usr/share/autodoers/hgbuildvdsmrpm'
#BUILDIMGCMD = '/usr/share/autodoers/hgbuildimg'

UPDATEREPOFROMSRC = '/usr/local/sbin/hgmakeproductrepo'
UPDATEREPOFROMGIT = '/usr/local/sbin/hgappendrpm'

OVIRTCACHEDIR = '/ovirt-cache/'

PROJECT_DICT = { 'vdsm':{'url':'git@192.168.1.200:/home/git/GitBase/vdsm','dir':'/usr/local/git/vdsm/', 'buildFromGit': 'yes'},
                 'ovirt-node':{'url':'git@192.168.1.200:/home/git/GitBase/ovirt-node','dir':'/usr/local/git/ovirt-node/','buildFromGit': 'yes'}}
