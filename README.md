# Archive reconstruction

The GO project has been relying on SVN, CVS and archive.geneontology.org for a long time.

The refactoring of GO requires a reorganization of some of the underlying infrastructures and remapping of old files into more up-to-date folder hierarchy (see current.genontology.org).

Full archive generated from SVN and CVS: https://geneontology-test.s3.amazonaws.com/index.html

## GO archive content
* CVS: 2002-2011 (ontology, slims, annotations)
* SVN: 2011-2018 (ontology, slims, annotations)
* archive.geneontology.org (all mysql dumps)

Notes:
* OBO files: gene_ontology.obo (v1.0, starts 2004-02); gene_ontology_ext.obo = current go.obo (starts 2009-03); other obo files discarded (gene_ontology-edit.obo, gene_ontology-write.obo, gene_ontology-1.2.obo)
* Slims: only obo slims were kept (starts mid 2004); archived_slims discarded (starts in 2003)

## SVN reconstruction steps / usage

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

Note: there will be some "Error while copying file" as we have to handle different file hierarchies over time (eg gene_association.goa_chicken.gz that became goa_chicken.gaf.gz and the script will be looking for both). Therefore, one should not be too concerned about those messages but they are still useful for debugging / logging of events.

## CVS reconstruction steps / usage
1. Have a GO CVS up and running
2. Create 1 revision / month
3. Remap the GO CVS data to a newer folder hierarchy:
`python create_archive_from_cvs.py -m <mapping_file> -s <svn_checkout_rep> -c <cvs_checkout_rep> -o <output_rep>

## Example of files currently generated
Release generated from CVS: https://geneontology-test.s3.amazonaws.com/2005-12-01/index.html
Release generated from SVN: https://geneontology-test.s3.amazonaws.com/2012-12-01/index.html

Note: browsing of the S3 bucket is inspired from [aws-js-s3-explorer](https://github.com/awslabs/aws-js-s3-explorer) but was remodeled to fit a canonical URL model and add the desired header / description. [Actual browser code](https://github.com/lpalbou/aws-js-s3-explorer)

## Requirements
* requests python library: `pip install requests`
* svn python library: `pip install svn`
