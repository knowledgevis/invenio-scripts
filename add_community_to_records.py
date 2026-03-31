import requests
import json

# Global variable for the Invenio API server root
INVENIO_SERVER_ROOT = "https://localhost:5000"
good_records = ['jt4jz-yat93']
good_records = []
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


def load_all_communities():
    """
    Query the Invenio API for all communities and populate the global
    communities_by_name dictionary, keyed by community name with the
    community ID as the value.

    Returns:
        dict: The populated communities_by_name dictionary
    """
    communities_by_name = {}
    communities_by_id = {}
    response = query_invenio_api('/api/communities')
    hits = response.get('hits', {}).get('hits', [])
    for community in hits:
        name = community.get('metadata', {}).get('title', '')
        community_id = community.get('id', '')
        if name:
            communities_by_name[name] = community_id
            communities_by_id[community_id] = name
                
    return communities_by_name, communities_by_id


def write_communities_csv(communities):
    """
    Write the communities dictionary to a CSV file named 'communities.csv'.
    Each row contains the community name and its corresponding ID.
    """
    csv_filename = 'communities.csv'
    with open(csv_filename, 'w') as csv_file:
        csv_file.write('community_name,community_id\n')
        for name, community_id in communities.items():
            csv_file.write(f'{name},{community_id}\n')
    print(f'Wrote {len(communities)} communities to {csv_filename}')


def find_all_invenio_records():
    """
    Find all records in the Invenio instance and return them as a list.
    
    Returns:
        list: A list of all records found in the Invenio instance
    """
    list_response = list_records()
    print('Found {} records.'.format(list_response['hits']['total']))
    return list_response


def write_single_csv_of_records(records, filename='records.csv'):    
    """
    Write a list of records to a single CSV file.
    
    Args:
        records (list): A list of record objects to write to the CSV file
        filename (str, optional): The name of the CSV file to write to (default is 'records.csv')
    """
    with open(filename, 'w') as csv_file:
        csv_file.write('record_id,community,title\n')
        for record in records:
            record_id = record['id']
            title = record['metadata'].get('title', '')
            try:
                #"communities": "https://xxx/api/records/jt4jz-yat93/communities",
                community_response = query_invenio_api(f'/api/records/{record_id}/communities')
                community_id   = community_response['hits']['hits'][0]['id'] if community_response['hits']['hits'] else 'unknown'
                community = communities_id.get(community_id, '')
            except Exception:
                community = ''
            csv_file.write(f'{record_id},"{community}","{title}"\n')
    print(f'Wrote {len(records)} records to {filename}')



def save_good_records(all_records,good_records=good_records):
    """
    save good records to JSON files named after their record IDs.
    """
    list_response = all_records

    for record in list_response['hits']['hits']:
        record_id = record['id']
        print('record id',record_id)

        if record_id in good_records:
            print('found a good record',record_id)
            title = record['metadata'].get('title', '')
            print('title',title)
            try:
                community = record['metadata'].get('communities', {}).get('ids', [])[0]
            except Exception as e:
                community = 'unknown'
            print('community',community)
            
            # Save the record object to a JSON file named after its record ID
            json_filename = f'{record_id}.json'
            with open(json_filename, 'w') as json_file:
                json.dump(record, json_file, indent=2)
            print(f'Saved record to {json_filename}')


def find_all_records_and_save_good_records(good_records=good_records):
    """
    Find all records in the Invenio instance and save them to JSON files named after their record IDs.
    """
    list_response = list_records()
    print('Found {} records.'.format(list_response['hits']['total']))

    for record in list_response['hits']['hits']:
        record_id = record['id']
        print('record id',record_id)

        if record_id in good_records:
            print('found a good record',record_id)
            title = record['metadata'].get('title', '')
            print('title',title)
            try:
                community = record['metadata'].get('communities', {}).get('ids', [])[0]
            except Exception as e:
                community = 'unknown'
            print('community',community)
            
            # Save the record object to a JSON file named after its record ID
            json_filename = f'{record_id}.json'
            with open(json_filename, 'w') as json_file:
                json.dump(record, json_file, indent=2)
            print(f'Saved record to {json_filename}')

communities_id = {}
communities = {}

def find_and_save_all_communities():
    """
    Find all communities in the Invenio instance and save them to a single CSV file.
    """
    global communities, communities_id
    communities,communities_id = load_all_communities()
    print(f'Found {len(communities)} communities.')
    write_communities_csv(communities)


def create_draft_from_published_record(record_id):
    pass



find_and_save_all_communities()
all_records = find_all_invenio_records()
write_single_csv_of_records(all_records['hits']['hits'])
save_good_records(all_records, good_records=good_records)

