import requests
import json
from grobid_client.grobid_client import GrobidClient
import os
import time
import argparse
import logging
import builtins
from datetime import datetime

from dotenv import load_dotenv
import openai
import pdfplumber
from io import BytesIO


logger = logging.getLogger("invenio_import")


def setup_logging(log_file_name):
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def print(*args, **kwargs):
    builtins.print(*args, **kwargs)
    if logger.handlers:
        sep = kwargs.get("sep", " ")
        message = sep.join(str(arg) for arg in args)
        logger.info(message)

# set up a log file with the name invenio-import-log-<datetime>.txt in the current directory
def parse_args():
    parser = argparse.ArgumentParser(description="Import local PDF metadata and files into Invenio.")
    parser.add_argument(
        "--log-file",
        dest="log_file",
        default=None,
        help="Log file name. Default: invenio-import-log-<datetime>.txt",
    )
    parser.add_argument(
        "--input-directory-path",
        dest="input_directory_path",
        default="/media/clisle/ExtremeSSD/NIAID-Axle/paper_import_test",
        help="Directory containing PDF and GROBID JSON files.",
    )
    args = parser.parse_args()

    if not args.log_file:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        args.log_file = f"invenio-import-log-{timestamp}.txt"

    return args



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

        # generate summary of the paper content using the OpenAI API and add it to the metadata dictionary for the record
        filepath = os.path.join(input_directory_path, PDFfile)
        extracted_text = extract_text_and_generate_summary(filepath)
       
        json_file = os.path.join(input_directory_path, PDFfile.replace(".pdf", ".json"))
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                metadata = json.load(f)
                metadata_dict[PDFfile] = metadata
                # convert the record to the format expected by the Invenio API
                print('converting record to Invenio format')
                invenio_records = CreateDraftRecordsWithMetadata(metadata_dict[PDFfile], auto_extracted_text=extracted_text)
                print('uploading record to Invenio API')
                for record in invenio_records:
                    #print(record)
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
                                    print(f"Successfully uploaded and committed file {PDFfile} to record ")
                                    print('attempting to publish record')
                                    publish_response = requests.post(f"{INVENIO_SERVER_ROOT}/api/records/{response['id']}/draft/actions/publish",
                                                                    headers=invenio_upload_headers,
                                                                    verify=False)
                                    if publish_response.status_code == 202:
                                        print(f"Successfully published record")
                        else:
                            print(f"Error creating file slot for {PDFfile}: {add_file_response.text}")
        else:
            print(f"No GROBID metadata JSON found for {PDFfile}")

    return responses_log


# for each key in the metadata_dict, create a draft record with the metadata and the description field set to the abstract
def CreateDraftRecordsWithMetadata(metadata_dict, auto_extracted_text=None):
    draft_records = []
    paper_metadata = metadata_dict
    # create a new draft record through the API with the metadata and the description field set to the abstract

    metadata = {
        "metadata" :{
            "title": paper_metadata['biblio']['title'] if 'biblio' in paper_metadata and 'title' in paper_metadata['biblio'] else "Sample Title",
            "description": auto_extracted_text if auto_extracted_text else (paper_metadata['biblio']['abstract'][0]['text'] if 'biblio' in paper_metadata and 'abstract' in paper_metadata['biblio'] else "Sample Abstract"),
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

    # add authors - there could be multiple authors, add a subrecord for each author.
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


# PDF Summarizer using OpenAI API

def messages_for(user_prompt):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

# with this prompt, the OpenAI model returned text in the outline form.  I wanted more of a plain text summary,
# see the revised version below.

system_prompt = """You are a research summarizer that summarizes the content of the research paper in no more than 1500 words. The research summary that you provide should include the following:
1) Objective/Problem - State the research goal or question.
2) Background - Briefly explain the context and significance.
3) Methods - Summarize the approach or methodology.
4) Key Findings - Highlight the main results or insights.
5) Conclusion - Provide the implications or contributions of the study.
6) Future Directions - Suggest areas for further research or exploration.
8) Limitations - Highlight constraints or challenges in the study.
Keep all points concise, clear, and focused and generate output in plain text."""

# revised system prompt
system_prompt = """You are a research summarizer that summarizes the content of the research paper in no more than 1500 words. 
The research summary that you provide should brieflly state the research goal or question, explain the context 
and significance, summarize the approach or methodology, highlight the main results or insights, 
provide the implications or contributions of the study, suggest areas for further research or exploration, 
and highlight constraints or challenges in the study.
Keep all points concise, clear, and focused and generate output in one or more paragraphs. Start immediately with facts from the paper 
content in the first sentence. Do not begin with "This research paper..." or similar pretext. Generate output in plain text.
Insert one blank line between paragraphs. Do not use bullet points or numbered lists. Do not include section headers. 
Generate the output in plain text format only, without any markdown formatting."""


def SummarizePDFWithOpenAI(user_prompt):
     # Generate messages using the system and user_prompt together
    messages = messages_for(user_prompt)
    start_time = time.perf_counter()

    print('sending extracted text to OpenAI API for summarization...')
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Correct model name
            messages=messages,
            max_tokens = 2000 # Pass the generated messages
        )
        # Return the content from the API response correctly
        print('received response from OpenAI API')

        # extract token usage information if available and print it
        usage = getattr(response, "usage", None)
        if usage is not None:
            prompt_tokens = getattr(usage, "prompt_tokens", None)
            completion_tokens = getattr(usage, "completion_tokens", None)
            total_tokens = getattr(usage, "total_tokens", None)
            print(
                "OpenAI token usage - "
                f"prompt: {prompt_tokens}, completion: {completion_tokens}, total: {total_tokens}"
            )
        else:
            print("OpenAI token usage not available in response")
        return response.choices[0].message.content
    except Exception as e:
        # Instead of printing, return an error message that can be displayed
        return f"Error in OpenAI API call: {e}"
    finally:
        elapsed_seconds = time.perf_counter() - start_time
        print(f"SummarizePDFWithOpenAI elapsed time: {elapsed_seconds:.2f} seconds")
    

def extract_text_and_generate_summary(filename):
        print(f"Extracting text from PDF file: {filename} for summary generation")
        pdf_file = filename
        # Extract text from the PDF
        try:
            with pdfplumber.open(pdf_file) as pdf:
                extracted_text = "\n".join(page.extract_text() for page in pdf.pages)
                extracted_text = extracted_text.replace("\n", " ")  # Replace newlines with spaces for better summarization
                # if the exracted text has non-ASCII characters, encode it to utf-8 to avoid issues with the OpenAI API
                extracted_text = extracted_text.encode('utf-8')    

            user_prompt = (
                f"You are looking at the text from a research paper. Summarize it in no more than 1500 words. "
                f"The output should be in plain text.\n\n{extracted_text}"
            )
            # Get the summarized response
            response = SummarizePDFWithOpenAI(user_prompt)        
            if response:
                return response
        except Exception as e:
            # If there's an error, print but return None so the paper abstract will be used instead
            print(f"**Error:** {str(e)}")
            return None


    
# ----------------- main execution -----------------
def main():
    args = parse_args()
    setup_logging(args.log_file)
    print(f"Logging to file: {args.log_file}")

    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print('No API key was found')
        return
    if not api_key.startswith("sk-proj-"):
        print("API key is found but is not in the proper format")
        return

    print("API key found and looks good so far")
    client = openai.OpenAI(api_key=api_key)
    globals()["openai"] = client

    paper_uploads = ExtractMetadataFromLocalFiles(args.input_directory_path)
    print('Upload complete')
    #print(paper_uploads)


if __name__ == "__main__":
    main()


