import os, json, sys, getopt
from datetime import datetime

import go_utils as utils

# require https://pypi.org/project/svn/
# note: could just run a process to have more control over the commands (eg can not --ignore-externals or --non-recursive)
# this would be much faster as there are several subfolders that we are not interested in for this archive reconstruction
# examples: https://stackoverflow.com/a/50980/7608507 and https://stackoverflow.com/a/16574107/7608507
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


def checkout(svn_base_url, revisions, output_rep):
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
            r = svn.remote.RemoteClient(svn_base_url + 'trunk/ontology/')
            r.checkout(output_rep + date + "/ontology/", revision)
        except Exception as err:
            print("Error while checking revision ", revision , ": " , err)

        try:
            r = svn.remote.RemoteClient(svn_base_url + 'trunk/external2go/')
            r.checkout(output_rep + date + "/external2go/", revision)
        except Exception as err:
            print("Error while checking revision ", revision , ": " , err)

        try:
            r = svn.remote.RemoteClient(svn_base_url + 'trunk/gene-associations/')
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

            # copy the whole folder and subfolders
            if filein.endswith("/"):
                utils.copy_folder(checkout_rep + release + "/" + filein, output_rep + release + "/" + fileout)

            # copy the file with specific extension
            elif "*." in filein:
                extension_in = filein[filein.rindex("/") + 1:] if "/" in filein else filein
                repin = filein.replace(extension_in, "")

                # check if we want to replace the extension
                extension_out = None
                repout = fileout
                if "*." in fileout:
                    extension_out = fileout[fileout.rindex("/") + 1:] if "/" in fileout else fileout
                    repout = fileout.replace(extension_out, "")
                utils.copy_files(checkout_rep + release + "/" + repin, extension_in, output_rep + release + "/" + repout, extension_out)
            
            # copy the file to another specific file
            else:
                utils.copy_file(checkout_rep + release + "/" + filein, output_rep + release + "/" + fileout)


    

def print_help():
    print('\nUsage: python create_archive.py -s <svn_base_url> -r <target_revisions> -m <mapping_file> -c <checkout_rep> -o <output_rep>\n')
    print('Example of svn_base_url: https://192.168.0.100/svn/go/\n')

def main(argv):
    target_revisions = ''
    checkout_rep = ''
    output_rep = ''
    svn_base_url = ''
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
            svn_base_url = arg
            if not svn_base_url.endswith("/"):
                svn_base_url += "/"
        elif opt in ("-m", "--mapping"):
            mapping_file = arg


    # create default folders (if needed)
    output_rep = utils.check_folder(output_rep)
    checkout_rep = utils.check_folder(checkout_rep)

    # get target revisions from svn.log and grep (see README.md)
    revisions = get_revisions(target_revisions)

    # checkout those revisions (if checkout already done, comment that line to proceed with the reconstruction)
    # checkout(svn_base_url, revisions, checkout_rep)

    # get mapping
    mapping = get_mappings(mapping_file)

    # map revisions to new folder
    map(mapping, checkout_rep, output_rep)

if __name__ == "__main__":
   main(sys.argv[1:])
