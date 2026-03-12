import requests
import json

# Global variable for the Invenio API server root
INVENIO_SERVER_ROOT = "https://localhost:5000"
good_records = ['6hb85-03457','nn041-vq357','67z73-phc25']
authorization_token = {'Authorization': 'Bearer PIErNEHI2tLp8yLl8R8QofSCEPgn0kCp7bPxXKXqFjMed2SvdQO7tniLtWoB'}


def query_invenio_api(endpoint, params=None):
    """
    Query the local Invenio API.
    
    Args:
        endpoint (str): The API endpoint (e.g., '/api/records', '/api/users')
        params (dict, optional): Query parameters to pass to the API
    
    Returns:
        dict: The JSON response from the API
    
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    # Construct the full API URL
    api_url = f"{INVENIO_SERVER_ROOT}{endpoint}"
    
    # Make the request
    response = requests.get(api_url, params=params, headers=authorization_token, verify=False)
    response.raise_for_status()
    
    # Return the result in JSON format
    return response.json()

def list_records(): 
    """
    List all records from the Invenio API.
    
    Returns:
        dict: The JSON response containing the list of records
    """
    return query_invenio_api('/api/records')



def delete_record(record_id):
    """
    Delete a record from the Invenio API.
    
    Args:
        record_id (str): The ID of the record to delete
    
    Returns:
        dict: The JSON response from the API
    
    Raises:
        requests.exceptions.RequestException: If the API request fails
    """
    # Construct the full API URL
    api_url = f"{INVENIO_SERVER_ROOT}/api/records/{record_id}"
    
    # Make the request
    response = requests.delete(api_url,headers=authorization_token)
    #response.raise_for_status()
    print(response.text)

    # Return the result in JSON format
    #return response.json()

list_response = list_records()
print('Found {} records.'.format(list_response['hits']['total']))
print('found fields',list_response.keys())

for record in list_response['hits']['hits']:
    record_id = record['id']
    print('record id',record_id)


# now attempt to delete all records that are not the PDFs I uploaded
for record in list_response['hits']['hits']:
    record_id = record['id']
    if record_id not in good_records:
        print('deleting record with id {}'.format(record_id))
        delete_response = delete_record(record_id)
        print('delete response',delete_response)
        