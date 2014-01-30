#!/usr/bin/python
import sys, os, pwd
import argparse, shlex
import plistlib


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
        return self.user_info.pw_dir


def main():

    # whoami != root?
    if os.getuid() != 0:
        
        print sys.argv[0], "requires root privileges."
        return -1
        
    else:
        
        # 12 args looks like casper suite
        if len(sys.argv) == 12:
            # casper: ignoring (mountpoint, computername, username)

            # merge parameters into argv
            argv = shlex.split(sys.argv[4])
            # print "Casper", argv
        else:
            # standard: ignoring script name
            argv = sys.argv[1:]

        parser = argparse.ArgumentParser(description='Provides administrative tools for intosystems.')
        parser.add_argument('-a', '--add', nargs='*', help='Add Spotlight exclusion')
        parser.add_argument('-d', '--delete', nargs='*', help='Delete Spotlight exclusion')

        args, unknown = parser.parse_known_args(argv)
        print args, unknown
    
        # determine current console user
        me = UserManager()

        if(args.add or args.delete):

            spotlight_config = "/.Spotlight-V100/VolumeConfiguration.plist"
        
            try:
                spotlight_data = plistlib.readPlist(spotlight_config)
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
                    if(path[0] == "~"):
                        
                        path = os.path.join(me.home_dir(), path[2:])
                        
                    # when path ends with / remove /
                    if(path[-1] == "/"):
                        path = path[:-1]

                    if(path in my_exclusions):
                        print "Ignoring", path
                    else:
                        print "Adding", path
                        my_exclusions.append(path)

            if args.delete:

                for path in args.delete:
                    # when path starts with ~ add user_name
                    if(path[0] == "~"):
                        path = os.path.join(me.home_dir(), path[2:])

                    # when path ends with / remove /
                    if(path[-1] == "/"):
                        path = path[:-1]
                        
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