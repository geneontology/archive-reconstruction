# Archive reconstruction

The GO project has been relying on SVN, CVS and archive.geneontology.org for a long time.

The refactoring of GO requires a reorganization of some of the underlying infrastructures and remapping of old files into more up-to-date folder hierarchy (see current.genontology.org).

## Steps / Usage

1. Have a GO SVN up and running
2. List all revision from SVN:
`svn log <svn-url/svn/go/trunk> > gosvn.log` to create the list of revisions
3. Clean up the log: 
`more gosvn.log | grep '^r[0-9]' > gosvn.list`
4. Create 1 revision / month: 
`python3 select_revisions.py -r gosvn.list -o revisions_target.list`
5. Remap the GO SVN data to a newer folder hierarchy:
`python3 create_archive.py -s <svn-base-url> -r revisions_target.list -m mapping.txt -c checkouts/ -o releases/`

This will checkout the selected revisions in `revisions_target.list` and remap them from the temporary checkout folder `checkouts/` to the new folder `releases/` using the `mapping.txt` mapping rules

## Requirements
* requests python library: `pip install requests`
* svn python library: `pip install svn`