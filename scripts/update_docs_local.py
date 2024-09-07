import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define SCOPES for Google Docs and Google Drive API access
SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly',  # Google Docs read-only access
    'https://www.googleapis.com/auth/drive.readonly'       # Google Drive read-only access
]

# Dictionary to store document names and their respective Google Docs IDs
DOCS = {
    'functional_requirements': '1NxX7krtwGDKubcgMhywKqDutGe2N-S4RxEhr5U7UBcQ',
    'system_block_diagram': '1_jM4hqGpjIw_PULmp0QU2PRDqzd9vfIFmgAreEXpT6Y',  # Add more documents here
}

# Load paths from environment variables, defaulting to the current folder if not set
credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', './credentials.json')
token_path = os.getenv('GOOGLE_TOKEN_PATH', './token.pickle')

# Path for the docs folder and last modified tracking folder
DOCS_FOLDER_PATH = '../docs/'
LAST_MODIFIED_FOLDER = './last_modified/'

def authenticate_google_docs_api():
    creds = None
    # Load credentials from token.pickle if available
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, log in using OAuth2
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_document_metadata(service, document_id):
    # Get the metadata for the document
    doc = service.documents().get(documentId=document_id).execute()
    last_modified_time = doc['revisionId']  # Use the revisionId to check last modified time
    return last_modified_time

def download_document(creds, document_name, document_id):
    # Use Google Drive API to download the document
    drive_service = build('drive', 'v3', credentials=creds)
    request = drive_service.files().export_media(fileId=document_id, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    # Define the local file path using the document name
    local_file_path = os.path.join(DOCS_FOLDER_PATH, f'{document_name}.docx')

    # Execute the request to get the file's content
    response = request.execute()

    # Save the file locally
    with open(local_file_path, 'wb') as file:
        file.write(response)

    print(f"Downloaded and saved {document_name}.docx")

def main():
    # Authenticate with Google Docs API
    creds = authenticate_google_docs_api()
    service = build('docs', 'v1', credentials=creds)

    # Ensure the docs and last_modified directories exist
    if not os.path.exists(DOCS_FOLDER_PATH):
        os.makedirs(DOCS_FOLDER_PATH)
    if not os.path.exists(LAST_MODIFIED_FOLDER):
        os.makedirs(LAST_MODIFIED_FOLDER)

    # Iterate over each document in the DOCS dictionary
    for document_name, document_id in DOCS.items():
        print(f"Checking {document_name}...")

        # Get the metadata for the current document
        last_modified_time = get_document_metadata(service, document_id)

        # Define the path to store the last modified time for each document
        last_modified_file = os.path.join(LAST_MODIFIED_FOLDER, f'{document_name}_last_modified.txt')

        # Load the last known state (last modified time) if it exists
        if os.path.exists(last_modified_file):
            with open(last_modified_file, 'r') as f:
                last_known_modified_time = f.read().strip()
        else:
            print(f"No last_modified file found for {document_name}. It will be created after downloading the document.")
            last_known_modified_time = None

        # If the document has been modified, download and replace it locally
        if last_modified_time != last_known_modified_time:
            print(f"{document_name} has been modified, downloading updated version...")
            download_document(creds, document_name, document_id)

            # Update the last known modified time
            with open(last_modified_file, 'w') as f:
                f.write(last_modified_time)
            print(f"Updated {document_name}_last_modified.txt with the new modified time.")

            # Optionally: Git commit the updated file
            local_file_path = os.path.join(DOCS_FOLDER_PATH, f'{document_name}.docx')
            os.system(f'git add {local_file_path}')
            os.system(f'git commit -m "Updated {document_name} document to the latest version"')
            print(f"Document {document_name} updated and committed to Git.")
        else:
            print(f"No changes detected in {document_name}.")

if __name__ == '__main__':
    main()
