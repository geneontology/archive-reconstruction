import json, sys, getopt, os
from datetime import datetime

import go_utils as utils

def get_revisions(file):
    rev_data = None
    with open(file, 'r', encoding='windows-1252') as myfile:
        rev_data = myfile.read()

    if rev_data is None:
        return None

    lines = rev_data.split("\n")
    revisions = []
    for line in lines:
        if len(line.strip()) == 0:
            continue
        split = line.split("|")
        date = split[2].strip()
        date_trim = date[0:date.rindex(":") + 3].strip()
        date = datetime.fromisoformat(date_trim)

        obj = {
            "revision": split[0].strip(),
            "user": split[1].strip(),
            "date": date,
            "date_str" : date_trim
        }
        revisions.append(obj)

    return revisions
    
def get_first_of_each_month(revisions):
    first = []

    last = None
    for revision in revisions:
        if len(first) == 0:
            first.append(revision)
            last = revision
        elif last is not None and (revision['date'].month - last['date'].month) != 0:
            first.append(revision)
            last = revision
    return first


def print_help():
    print('\nUsage: python select_revisions.py -r <revision_file> -o <output>\n')

def main(argv):
    revision_file = ''
    output_file = ''

    if len(argv) < 4:
        print_help()
        sys.exit(2)

    try:
        opts, argv = getopt.getopt(argv,"r:o:",["revision=", "output="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-r", "--revision"):
            revision_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg


    # creating revisions object
    revisions = get_revisions(revision_file)
    if revisions is None:
        print("Could not get revisions from ", revision_file)
        sys.exit(2)

    # sort by ascending order
    revisions = sorted(revisions, key=lambda x: x['date'], reverse=False)

    # get 1 revision / month
    first_revisions = get_first_of_each_month(revisions)

    report = []
    for rev in first_revisions:
#        report.append(rev['date'].strftime("%Y-%m-%d") + "\t" + rev['date_str'] + "\t" + rev['revision'])
        report.append(rev['date_str'] + "\t" + rev['revision'] + "\t" + rev['user'])
    
    report = "\n".join(report)
    utils.write_text(output_file, report)


if __name__ == "__main__":
   main(sys.argv[1:])
   