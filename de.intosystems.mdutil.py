#!/usr/bin/python
import sys
import os
import pwd
import shlex
import argparse
import plistlib
import subprocess


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
        
    def home_dir(self):
        return os.path.expanduser('~' + self.user_name)


def main():

    # whoami != root?
    if os.getuid() != 0:
        
        print sys.argv[0], "requires root privileges."
        return -1
        
    else:
        
        parser = argparse.ArgumentParser(description='Provides administrative tools for intosystems.')
        parser.add_argument('-a', '--add', nargs='*', help='Add Spotlight exclusion')
        parser.add_argument('-d', '--delete', nargs='*', help='Delete Spotlight exclusion')

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

        args, unknown = parser.parse_known_args(args)
        # print args, unknown
    
        # determine current console user
        me = UserManager()

        if(args.add or args.delete):

            spotlight_config = "/.Spotlight-V100/VolumeConfiguration.plist"
        
            try:
                p = subprocess.Popen(['/usr/bin/plutil','-convert','xml1', '-o', '-', spotlight_config], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out_data, err_data = p.communicate()
                
                if(p.returncode == 0):
                    spotlight_data = plistlib.readPlistFromString(out_data)
                else:
                    spotlight_data = {}
                    
            except IOError as e:
                # file could not be found
                print e
                # creating our own data
                spotlight_data = {}
                
            my_exclusions = spotlight_data.get('Exclusions', [])
            print "Current settings", my_exclusions

            if args.add:

                for path in args.add:
                    # when path starts with ~ add user_name
                    if(path[0:2] == ("~" + os.sep)):
                        path = os.path.join(me.home_dir(), path[2:])
                        
                    # Normalize path
                    path = os.path.normpath(path)

                    if(path in my_exclusions):
                        print "Ignoring", path
                    else:
                        print "Adding", path
                        my_exclusions.append(path)

            if args.delete:

                for path in args.delete:
                    # when path starts with ~ add user_name
                    if(path[0:2] == ("~" + os.sep)):
                        path = os.path.join(me.home_dir(), path[2:])

                    # Normalize path
                    path = os.path.normpath(path)
                        
                    if(path in my_exclusions):
                        print "Removing", path
                        my_exclusions.remove(path)
                    else:
                        print "Ignoring", path

            print "New settings", my_exclusions
            spotlight_data.update({'Exclusions': my_exclusions})
        
            try:
                plistlib.writePlist(spotlight_data, spotlight_config)
            except TypeError as e:
                print e
                return 1

        else:
            parser.print_help()
            
        return 0


if __name__ == '__main__':
    sys.exit(main())