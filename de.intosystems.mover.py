#!/usr/bin/python

import sys
import syslog
import os
import pwd
import argparse
import shutil
import shlex

class UserManager(object):
    """docstring for UserManager"""
    def __init__(self, user=None):
        super(UserManager, self).__init__()
        self.user = user
        
        try:
            self.user_info = self.console_user()
                
        except KeyError as e:
            syslog.syslog(syslog.LOG_ERR, "Error: " + str(e))

        self.user_name = self.user_info.pw_name
    
    # determine current user
    def console_user(self):
        status = os.stat('/dev/console')
        uid = status.st_uid
        return pwd.getpwuid(uid)

    def uid(self):
        return self.user_info.pw_uid

    def gid(self):
        return self.user_info.pw_gid

class FileManager(object):
    """docstring for FileManager"""
    def __init__(self, path=os.getcwd(), user=UserManager().user_name):
        super(FileManager, self).__init__()
        
        if(path):

            # separate path and filename
            (pathname, filename) = os.path.split(path)
            # print pathname, filename

            # path starts with a tilde
            if(pathname and pathname[0] == "~"):
                # get os separator like "/"
                seperator = os.sep
                
                # split path by separator
                path_components = pathname[1:].split(seperator)
                # print "path_components", path_components
            
                # get home directory for user_name
                user_name = user
                user_home = os.path.expanduser('~' + user_name)
                # print user_home

                # join home directory and path as path
                path = os.path.join(user_home, *path_components)
                path = os.path.join(path, filename)
                # print path
        
        self.path = path
        # print self.path

    def move(self, dest):
        src = self.path
        dest = os.path.expanduser(dest)

        if(os.path.exists(src)):
            
            try:
                shutil.move(src, dest)
                syslog.syslog(syslog.LOG_ERR, "MOVING SRC: " + src + " DEST: " + dest)
            except shutil.Error as e:
                syslog.syslog(syslog.LOG_ERR, "Error: " + str(e))
                

    def chmod(self, mode, rec=False):
        #convert input to base 8
        mode = int(str(mode), 8)

        print 'Filemode', oct(mode), 'for', self.path, rec
        os.chmod(self.path, mode)

        if(rec):
            # walk self
            for root, dirs, files in os.walk(self.path):
              for momo in dirs:
                # print os.path.join(root, momo)
                os.chmod(os.path.join(root, momo), mode)
              for momo in files:
                # print os.path.join(root, momo)
                os.chmod(os.path.join(root, momo), mode)
                

    def chown(self, uid=-1, gid=-1, rec=False):

        print 'chown', self.path, uid, gid, rec
        os.chown(self.path, uid, gid)

        if(rec):
            # walk self
            for root, dirs, files in os.walk(self.path):
              for momo in dirs:
                # print os.path.join(root, momo)
                os.chown(os.path.join(root, momo), uid, gid)
              for momo in files:
                # print os.path.join(root, momo)
                os.chown(os.path.join(root, momo), uid, gid)


def main():

    parser = argparse.ArgumentParser(description='Provides administrative tools for intosystems.')
    parser.add_argument('-r', '--recursive', action='store_true', help='Apply options (MODE, OWNERSHIP) recursive')
    parser.add_argument('-o', '--own', action='store_true', help='Own the file (USER/GROUP)')
    parser.add_argument('-m', '--mode', type=str)
    parser.add_argument('src', nargs='?', default=None, type=FileManager)
    parser.add_argument('dest', nargs='?', default=None, type=FileManager)

    argv = []

    if len(sys.argv) == 12:
        # casper: ignoring (mountpoint, computername, username)
        for arg in sys.argv[4:]:
            argv += shlex.split(arg)
        
    else:
        # standard: ignoring script name
        argv = sys.argv[1:]

    args, unknown = parser.parse_known_args(argv)
    # print args, unknown
    # sys.exit(0)
    
    if(args.src and args.dest):
    
        args.src.move(args.dest.path)
        
        if(args.mode):
            args.dest.chmod(args.mode, args.recursive)
            
        if(args.own):
            me = UserManager()
            user = me.uid()
            group = me.gid()
            args.dest.chown(user, group, args.recursive)
        
    else:
        parser.print_help()

if __name__ == '__main__':
    sys.exit(main())