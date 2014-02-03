#!/usr/bin/python
import CoreFoundation
import sys
import os
import pwd
import argparse
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


def forced(key, applicationID):
    return CoreFoundation.CFPreferencesAppValueIsForced(key, applicationID)

def getPrefs(key, applicationID, userName=CoreFoundation.kCFPreferencesAnyUser, hostName=CoreFoundation.kCFPreferencesCurrentHost):
    value = CoreFoundation.CFPreferencesCopyValue(
        key,
        applicationID,
        userName,
        hostName
    )
    return list(value) if value else []

def setPrefs(key, value, applicationID, userName=CoreFoundation.kCFPreferencesAnyUser, hostName=CoreFoundation.kCFPreferencesCurrentHost):
    return CoreFoundation.CFPreferencesSetValue(
        key,
        value,
        applicationID,
        userName,
        hostName
    )

def syncPrefs(applicationID, userName=CoreFoundation.kCFPreferencesAnyUser, hostName=CoreFoundation.kCFPreferencesCurrentHost):
    return CoreFoundation.CFPreferencesSynchronize(
       applicationID,
       userName,
       hostName
    )

def main():

    # whoami != root?
    if os.getuid() != 0:
        
        print sys.argv[0], "requires root privileges."
        return -1
        
    else:

        parser = argparse.ArgumentParser(description='Provides administrative tools for intosystems.')
        parser.add_argument('-c', '--clean', action='store_true', help='Clean forced Time Machine settings')
        parser.add_argument('-a', '--add', nargs='*', help='Add Time Machine exclusion')
        parser.add_argument('-d', '--delete', nargs='*', help='Delete Time Machine exclusion')

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

        args, unknown = parser.parse_known_args(argv)
        print args, unknown
    
        # determine current console user
        me = UserManager()

        # The ID of the application whose preferences we wish to modify.
        applicationID   = "com.apple.TimeMachine"

        # # defined by applications
        # # not shown in the GUI
        keyExclude      = "ExcludeByPath"

        # # defined by users
        # # shown in the GUI
        keySkip         = "SkipPaths"
        
        if(args.clean or args.add or args.delete):

            excludesByPath = getPrefs(keyExclude, applicationID)
            print "Current settings", excludesByPath

            if args.clean:
                
                if(forced(keyExclude, applicationID) or forced(keySkip, applicationID)):
                    # clean up mcx-settings
                    # skippedByPath = getPrefs(keySkip, applicationID)
                    pass

            if args.add:

                for path in args.add:
                    # when path starts with ~/, replace tilde with user_name
                    if(path[0:2] == "~/"):
                        path = '~' + str(me.user_name) + path[1:]
                        
                    # Normalize path
                    path = os.path.normpath(path)

                    if(path in excludesByPath):
                        print "Ignoring", path
                    else:
                        print "Adding", path
                        excludesByPath.append(path)

            if args.delete:

                for path in args.delete:
                    # when path starts with ~/, replace tilde with user_name
                    if(path[0:2] == "~/"):
                        path = '~' + str(me.user_name) + path[1:]
                        
                    # Normalize path
                    path = os.path.normpath(path)
                        
                    if(path in excludesByPath):
                        print "Removing", path
                        excludesByPath.remove(path)
                    else:
                        print "Ignoring", path

            print setPrefs(keyExclude, excludesByPath, applicationID)
            
            if(syncPrefs(applicationID)):
                print "New settings", getPrefs(keyExclude, applicationID)
                return 0
            else:
                print "ERROR: Could not write changes to permanent storage."
                return 1

        else:
            parser.print_help()
            
        return 0


if __name__ == '__main__':
    sys.exit(main())