import json, sys, getopt, os, shutil, glob
from datetime import datetime

import go_utils as utils

# require https://pypi.org/project/svn/
import svn.remote




def get_revisions(target_revisions):
    rev_data = None
    with open(target_revisions, 'r', encoding='windows-1252') as myfile:
        rev_data = myfile.read()
    revisions = rev_data.split("\n")
    return revisions

def get_mappings(mapping_file):
    tmp = None
    with open(mapping_file, 'r', encoding='windows-1252') as myfile:
        tmp = myfile.read()
    mapping = tmp.split("\n")
    return mapping


def checkout(revisions, output_rep):
    count = 1
    for line in revisions:
        split = line.split("\t")
        date = datetime.fromisoformat(split[0])
        date = date.strftime("%Y-%m-%d")
        revision = split[1]

        print("Checking revision " , revision , " (" , count , " / " , len(revisions) , ") ... in :")
        count += 1

        # note: we could do a single checkout for the whole trunk but this would take much more time
        try:
            r = svn.remote.RemoteClient('https://192.168.0.100/svn/go/trunk/ontology/')
            r.checkout(output_rep + date + "/ontology/", revision)
        except Exception as err:
            print("Error while checking revision ", revision , ": " , err)

        try:
            r = svn.remote.RemoteClient('https://192.168.0.100/svn/go/trunk/external2go/')
            r.checkout(output_rep + date + "/external2go/", revision)
        except Exception as err:
            print("Error while checking revision ", revision , ": " , err)

        try:
            r = svn.remote.RemoteClient('https://192.168.0.100/svn/go/trunk/gene-associations/')
            r.checkout(output_rep + date + "/gene-associations/", revision)
        except Exception as err:
            print("Error while checking revision ", revision , ": " , err)


def map(mapping, checkout_rep, output_rep):
    releases = os.listdir(checkout_rep)
    for release in releases:
        print("\n\nRemapping release ", release , " from " , checkout_rep , " to ", output_rep)
        for item in mapping:
            if len(item.strip()) == 0 or item.startswith("#"):
                continue
            split = item.split()
            filein = split[0]
            fileout = split[1]

            if filein.endswith("/"):
                copy_folder(checkout_rep + release + "/" + filein, output_rep + release + "/" + fileout)
            elif "*." in filein:
                extension = filein[filein.rindex("/") + 1:] if "/" in filein else filein
                rep = filein.replace(extension, "")
                copy_files(checkout_rep + release + "/" + rep, extension, output_rep + release + "/" + fileout)

from distutils.dir_util import copy_tree
def copy_folder(input_rep, output_rep):
    check_folder(output_rep)
    print("copy folder: ", input_rep , " -> " , output_rep)
    # shutil.copytree(input_rep, output_rep)  
    try:
        copy_tree(input_rep, output_rep)
    except Exception as err:
        print("could not copy folder: ", err)

def copy_files(input_rep, extension, output_rep):
    check_folder(output_rep)
    print("copy files: ", input_rep + extension , " -> " , output_rep)
    in_files = glob.glob(input_rep + extension)
    for in_file in in_files:
        ifile = in_file.replace(input_rep, "")
        try:
            shutil.copy(input_rep + "/" + ifile, output_rep + "/" + ifile)
        except Exception as err:
            print("could not copy file: ", err)


def copy_file(in_file, out_file, compress_out):
    """
    This will be used to remap a filename to another one during copy
    If required, will also compress the file
    """
    pass

def check_folder(folder):
    if not folder.endswith("/"):
        folder += "/"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder
    

def print_help():
    print('\nUsage: python create_archive.py -s <svn_server> -r <target_revisions> -m <mapping_file> -c <checkout_rep> -o <output_rep>\n')

def main(argv):
    target_revisions = ''
    checkout_rep = ''
    output_rep = ''
    svn_server = ''
    mapping_file = ''

    if len(argv) < 4:
        print_help()
        sys.exit(2)

    try:
        opts, argv = getopt.getopt(argv,"s:r:o:m:c:", ["svn=", "revision=", "output=", "mapping=", "checkout="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-r", "--revision"):
            target_revisions = arg
        elif opt in ("-o", "--output"):
            output_rep = arg
        elif opt in ("-c", "--checkout"):
            checkout_rep = arg
        elif opt in ("-s", "--svn"):
            svn_server = arg
        elif opt in ("-m", "--mapping"):
            mapping_file = arg


    output_rep = check_folder(output_rep)
    checkout_rep = check_folder(checkout_rep)


    # get target revisions
    revisions = get_revisions(target_revisions)

    # checkout those revisions
    # checkout(revisions, checkout_rep)

    # get mapping
    mapping = get_mappings(mapping_file)

    # map revisions to new folder
    map(mapping, checkout_rep, output_rep)

if __name__ == "__main__":
   main(sys.argv[1:])
