# invenio-scripts

This repository holds a collection of scripts used to work with the InvenioRDM Document management archive.
In most cases, they make use of the Invenio API () 

**upload-doc-from-local-file.py** - This python script takes an input directory of scientific papers and
uses the Invenio API to create records, upload metadata extracted from the PDF version of the paper, and publishes
the record so it is viewable and searchable for all users of this InvenioRDM instance.   Early versions of this 
script have hard-coded pathnames and were used just as a proof of concept for automatic import.  The Invenio
interface allows documents to be manually uploaded, but this is much more time consuming than automatic
document scraping and upload. 

**delete_metadata_records.py** - The first script developed to query InvenioRDM, find metadata-only records, 
which don't have files attached to them and delete the records.  This is handy to clean up the database when
the initial instantiation of Invenio uploads test records that are in the way later. 

