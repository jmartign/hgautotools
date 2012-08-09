#! /usr/bin/python

AUTOBUILDERLOGFILE = '/var/log/autobuilder.log'
AUTOCREATORLOGFILE = '/var/log/autocreator.log'

BAKLOGFILE = '/dev/stdout'

# for autobuilder
CVSTEMPDIR = '/home/autobuild/workspace/'
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


BUILDNODERPMCMD = '/usr/share/autocreator/hgbuildnoderpm'
BUILDVDSMRPMCMD = '/usr/share/autocreator/hgbuildvdsmrpm'
BUILDIMGCMD = '/usr/share/autocreator/hgbuildimg'
GETLASTIDCMD = '/usr/share/autocreator/hggetlastlog'

UPDATEREPOFROMSRC = '/usr/local/sbin/hgmakeproductrepo'
UPDATEREPOFROMGIT = '/usr/local/sbin/hgappendrpm'

OVIRTCACHEDIR = '/ovirt-cache/'

PROJECT_DICT = { 'vdsm':{'url':'git://192.168.0.200/vdsm','dir':'/usr/local/git/vdsm/', 'buildFromGit': 'yes'},
        'ovirt-node':{'url':'git://192.168.0.200/ovirt-node','dir':'/usr/local/git/ovirt-node/','buildFromGit': 'yes'}}

PRODUCT_DICT = { 'ctnode':
                         {
                             'branch':'ct_product',
                             'repodir':'/storage/creator/CTNode/product/',
                             'imagesdir': '/storage/BACKUP/ISO/ovirt/nightlybuild/',
                             'buildimgflag': '/var/run/ctnodebuildingimg.flag',
                             'updaterepobin' : '/usr/local/sbin/hgmakeproductrepo'
                         },
                 'bell':
                         {
                             'branch':'bell',
                             'repodir':'/storage/creator/Bell/product/',
                             'imagesdir': '/storage/BACKUP/ISO/ovirt/bell/nightlybuild/',
                             'buildimgflag': '/var/run/bellbuildingimg.flag',
                             'updaterepobin' : '/usr/local/sbin/hgmakebellrepo'
                         }
                }
