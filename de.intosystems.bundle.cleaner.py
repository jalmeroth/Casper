#!/usr/bin/python

import sys
import os
import shutil


def main():

    users = "/Users"
    docs = "Documents"
    bundle = "into_CD_Bundle"

    # clean out existing users
    for username in os.listdir(users):

        # /Users/ladmin/Documents/into_CD_Bundle
        bundle_path = os.path.join(users, username, docs, bundle)
        # print bundle_path

        if(os.path.exists(bundle_path)):
            # print "Trash me, if you can."
            trash = os.path.join(users, username, ".Trash")
            filename = bundle + "_" + str(os.getpid())
            bundle_trash = os.path.join(trash, filename)
            # print bundle_trash
            
            try:
                print "MOVING:", bundle_path, "to", bundle_trash
                shutil.move(bundle_path, bundle_trash)
            except shutil.Error as e:
                print "ERROR:", e
                
    templates = "/System/Library/User Template"

    # clean out template folders
    for template in os.listdir(templates):

        # /System/Library/User Template/German.lproj/Documents/into_CD_Bundle
        bundle_path = os.path.join(templates, template, docs, bundle)
        if(os.path.exists(bundle_path)):
            try:
                print "TRASHING:", bundle_path
                shutil.rmtree(bundle_path)
            except shutil.Error as e:
                print "ERROR:", e

if __name__ == '__main__':
    sys.exit(main())