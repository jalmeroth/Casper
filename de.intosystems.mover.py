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
    def __init__(self):
        super(UserManager, self).__init__()

        try:
            self.user_info = self.console_user()
            self.user_name = self.user_info.pw_name
                
        except KeyError as e:
            print "Error", e
    
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
        
        # save original input
        self.input_path = path
        
        # path starts with a tilde
        if(self.input_path[0:2] == ("~" + os.sep)):
            # get home directory for user_name
            user_name = user
            user_home = os.path.expanduser('~' + user_name)
            # print user_home

            # join home directory and path
            path = user_home + self.input_path[1:]
            # print "Full", path

        # Normalize path
        path = os.path.normpath(path)
        # print "normpath", path

        self.path = os.path.realpath(path)
        # print "realpath", self.path, self.walkit

    def move(self, dest, force=False):
        src = self

        if(os.path.exists(src.path)):
            
            # shutil.move: If the destination is a directory or a symlink to a directory,
            # the source is moved INSIDE the directory
            if(os.path.isdir(dest.path)):
                print "+++DEST: DIRECTORY+++"
                dest.target_path = os.path.join(dest.path, os.path.basename(src.path))
                print "NEW DEST", dest.target_path
            else:
                dest.target_path = dest.path
            
            if(os.path.exists(dest.target_path)):
                # override file
                if(force):
                    print "+++DEST: OVERWRITING+++"

                    if(os.path.isdir(dest.target_path)):
                        shutil.rmtree(dest.target_path)
                    
                    try:
                        return shutil.move(src.path, dest.path)
        
                    except (shutil.Error, OSError) as e:
                        print "ERROR", e
                        return 1

                else:
                    print "Destination path", dest.target_path, "already exists"
                
            else:
                print "MOVING SRC", src.path, "DEST", dest.path

                try:
                    return shutil.move(src.path, dest.path)
        
                except (shutil.Error, OSError) as e:
                    print "ERROR", e
                    return 1
                    
        else:
            print "Source does not exist.", src.path
            return 2

    def chmod(self, mode, rec=False):
        #convert input to base 8
        mode = int(str(mode), 8)

        # if path has changed while moving
        if(self.target_path):
            path = self.target_path
        else:
            path = self.path

        print 'Filemode', oct(mode), 'for', path, rec
        os.chmod(path, mode)

        if(rec):
            # walk self
            for root, dirs, files in os.walk(path):
              for momo in dirs:
                # print os.path.join(root, momo)
                os.chmod(os.path.join(root, momo), mode)
              for momo in files:
                # print os.path.join(root, momo)
                os.chmod(os.path.join(root, momo), mode)
                

    def chown(self, uid=-1, gid=-1, rec=False):

        # if path has changed while moving
        if(self.target_path):
            path = self.target_path
        else:
            path = self.path

        print 'chown', path, uid, gid, rec
        os.chown(path, uid, gid)

        if(rec):
            # walk self
            for root, dirs, files in os.walk(path):
              for momo in dirs:
                # print os.path.join(root, momo)
                os.chown(os.path.join(root, momo), uid, gid)
              for momo in files:
                # print os.path.join(root, momo)
                os.chown(os.path.join(root, momo), uid, gid)

def main():

    parser = argparse.ArgumentParser(description='Provides administrative tools for intosystems.')
    parser.add_argument('-f', '--force', action='store_true', help='Force override')
    parser.add_argument('-r', '--recursive', action='store_true', help='Apply options (MODE, OWNERSHIP) recursive')
    parser.add_argument('-o', '--own', action='store_true', help='Own the file (USER/GROUP)')
    parser.add_argument('-m', '--mode', type=str)
    parser.add_argument('src', nargs='?', default=None, type=FileManager)
    parser.add_argument('dest', nargs='?', default=None, type=FileManager)

    # 12 args looks like casper suite
    if len(sys.argv) == 12:
        # casper: ignoring (mountpoint, computername, username)
        argv = sys.argv[4:]
    else:
        # standard: ignoring script name
        argv = sys.argv[1:]

    # initialize args
    args = []
    
    # split arguments like bash would do
    for arg in argv:
        args += shlex.split(arg)
    
    # parse arguments
    args, unknown = parser.parse_known_args(args)
    # print args, unknown
    # sys.exit(0)
    
    if(args.src and args.dest):
        # print args.src.path
        # print args.dest.path

        e = args.src.move(args.dest, args.force)

        if(e):
            sys.exit(e)
        else:
            if(args.mode):
                args.dest.chmod(args.mode, args.recursive)
        
            if(args.own):
                me = UserManager()
                user = me.uid()
                group = me.gid()
                args.dest.chown(user, group, args.recursive)

        sys.exit(0)
        
    else:
        parser.print_help()

if __name__ == '__main__':
    sys.exit(main())