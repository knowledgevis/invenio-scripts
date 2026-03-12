import requests
import json
from grobid_client.grobid_client import GrobidClient
import os



# Global variable for the Invenio API server root
INVENIO_SERVER_ROOT = "https://localhost:5000"
invenio_upload_headers = {'accept': 'application/json',
                        'Content-Type': 'application/json',
                    'Authorization': 'Bearer PIErNEHI2tLp8yLl8R8QofSCEPgn0kCp7bPxXKXqFjMed2SvdQO7tniLtWoB'}
file_upload_headers = {'accept': 'application/json',
                    'Content-Type': 'application/octet-stream',
                    'Authorization': 'Bearer PIErNEHI2tLp8yLl8R8QofSCEPgn0kCp7bPxXKXqFjMed2SvdQO7tniLtWoB'}


# The process of importing a document from a local file to the Invenio API would typically involve the following steps:
# 1. Read the local file and extract its contents.
# 2. Create a new draft record through the API. This draft record should have an AI summary
#    added as the description field in the metadata. We will use the paper Abstract as a placeholder
# 
# 3. Add the file through the multistep process outlined 
#    in https://deepwiki.com/inveniosoftware/invenio-openapi/2.3-records-and-drafts-api
# 4. Publish the draft record to make it available in the Invenio repository.


# use GROBID to extract metadata from the local files in the directory, including the abstract 
# for the description field in the metadata

def ExtractMetadataFromLocalFiles(input_directory_path,maxConcurrency=4):
    # Use GROBID to extract metadata from the local file
    # This code assumes an external GROBID service is running and accessible at the specified URL
    grobid_url = "http://localhost:8070"
   
    # Initialize with custom server
    client = GrobidClient(grobid_server=grobid_url)

    # find all the PDF files in the input directory
    pdf_files = [f for f in os.listdir(input_directory_path) if f.endswith(".pdf")]

    # Process documents
    print(f"Processing {len(pdf_files)} PDF files with GROBID...")
    
    client.process(
        service="processFulltextDocument",
        input_path=input_directory_path,
        n=maxConcurrency,
        json_output=True
    )
    
    # read metadata back from output directory and return as a list of dictionaries
    metadata_dict = {}
    responses_log = []
    for PDFfile in pdf_files:
        json_file = os.path.join(input_directory_path, PDFfile.replace(".pdf", ".json"))
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                metadata = json.load(f)
                metadata_dict[PDFfile] = metadata
                # convert the record to the format expected by the Invenio API
                print('converting record to Invenio format')
                invenio_records = CreateDraftRecordsWithMetadata(metadata_dict)
                print('uploading record to Invenio API')
                for record in invenio_records:
                    print(record)
                    # upload the record to the Invenio API
                    response = UploadInvenioDraftRecord(record)
                    responses_log.append(response)
                    #print(f"Response from Invenio Record Creation: {response}")
                    if 'error' in response: 
                        print(f"Error uploading record for file {PDFfile}: {response['error']}")
                    else:
                        # upload the file to the record using the multistep process 
                        # outlined in the Invenio API documentation

                        # create the file key
                        filepath = os.path.join(input_directory_path, PDFfile)
                        file_key = [{"key": PDFfile}]
                        add_file_response = requests.post(f"{INVENIO_SERVER_ROOT}/api/records/{response['id']}/draft/files",    
                                                            headers=invenio_upload_headers, 
                                                            json=file_key, 
                                                            verify=False)
                        #print(f"Response from Invenio File Create Slot: {add_file_response.text}")
                        # now upload the file to the created slot
                        if add_file_response.status_code == 201:
                            file_content = {'file': open(filepath, 'rb')}
                            upload_file_response = requests.put(f"{INVENIO_SERVER_ROOT}/api/records/{response['id']}/draft/files/{PDFfile}/content",
                                                                headers=file_upload_headers,
                                                                files=file_content,
                                                                verify=False)
                            #print(f"Response from Invenio File Upload: {upload_file_response.text}")
                            # commit the file upload
                            if upload_file_response.status_code == 200:
                                commit_file_response = requests.post(f"{INVENIO_SERVER_ROOT}/api/records/{response['id']}/draft/files/{PDFfile}/commit",
                                                                    headers=invenio_upload_headers,
                                                                    verify=False)
                                #print(f"Response from Invenio File Commit: {commit_file_response.text}")
                                if commit_file_response.status_code != 200:
                                    print(f"Error committing file for {PDFfile}: {commit_file_response.text}")
                                else:
                                    print(f"Successfully uploaded and committed file {PDFfile} to record {response['id']}")
                                    print('attempting to publish record')
                                    publish_response = requests.post(f"{INVENIO_SERVER_ROOT}/api/records/{response['id']}/draft/actions/publish",
                                                                    headers=invenio_upload_headers,
                                                                    verify=False)
                                    if publish_response.status_code == 202:
                                        print(f"Successfully published record {response['id']}")
                        else:
                            print(f"Error creating file slot for {PDFfile}: {add_file_response.text}")
                        

    return responses_log


# for each key in the metadata_dict, create a draft record with the metadata and the description field set to the abstract
def CreateDraftRecordsWithMetadata(metadata_dict):
    draft_records = []
    for key in metadata_dict:
        print(f"Processing file: {key}")
        paper_metadata = metadata_dict[key]
        # create a new draft record through the API with the metadata and the description field set to the abstract

        metadata = {
            "metadata" :{
                "title": paper_metadata['biblio']['title'] if 'biblio' in paper_metadata and 'title' in paper_metadata['biblio'] else "Sample Title",
                "description": paper_metadata['biblio']['abstract'][0]['text'] if 'biblio' in paper_metadata and 'abstract' in paper_metadata['biblio'] else "Sample Abstract",
                "publication_date": paper_metadata['biblio']['publication_date'] if 'biblio' in paper_metadata and 'publication_date' in paper_metadata['biblio'] else "2026-01-01",
                "publisher": paper_metadata['biblio']['publisher'] if 'biblio' in paper_metadata and 'publisher' in paper_metadata['biblio'] else "Sample Publisher",
                "resource_type": {
                    "id": "publication-article",
                    "title": {
                    "cs": "Článek v časopise",
                    "de": "Zeitschriftenartikel",
                    "en": "Journal article",
                    "sv": "Tidskriftsartikel"
                    },
                }
            }
        }

        # add authors
        metadata['metadata']['creators'] = []
        for author in paper_metadata['biblio']['authors'] if 'biblio' in paper_metadata and 'authors' in paper_metadata['biblio'] else []:
            metadata['metadata']["creators"].append(
                {
                "person_or_org": {
                    "family_name": author.split(' ')[-1],
                    "given_name": author.split(' ')[0], 
                    "type": "personal",
                    #"identifiers": [ {"identifier":  "0000-0000-0000-0000", "scheme": "orcid"} ]
                    },
                    "affiliations": author['affiliation'] if 'affiliation' in author else "Unknown"
                }
                )
        draft_records.append(metadata)   
    return draft_records

# Now upload the draft records using the Invenio API, and add the file through the multistep process outlined 
# in https://deepwiki.com/inveniosoftware/invenio-openapi/2.3-records-and-drafts-api

def UploadInvenioDraftRecord(metadata):
    response = requests.post(f"{INVENIO_SERVER_ROOT}/api/records", json=metadata, headers=invenio_upload_headers,verify=False)
    try:
        response_json = response.json()
        return response_json
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response for record: {response.text}")
        return {'error': 'Failed to decode JSON response', 'response_text': response.text}




input_directory_path = "/media/clisle/ExtremeSSD/NIAID-Axle/paper_import_test"
paper_uploads = ExtractMetadataFromLocalFiles(input_directory_path)
print('Invenio responses log')
print(paper_uploads)


