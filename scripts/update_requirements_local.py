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

# Google Docs document ID (replace with your actual document ID)
DOCUMENT_ID = '1NxX7krtwGDKubcgMhywKqDutGe2N-S4RxEhr5U7UBcQ'

# Load paths from environment variables, defaulting to the current folder if not set
credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', './credentials.json')
token_path = os.getenv('GOOGLE_TOKEN_PATH', './token.pickle')

# Paths for credentials and token files
LOCAL_FILE_PATH = '../docs/functional_requirements.docx'  # Path where the Google Docs file will be saved locally
last_modified_file = 'last_modified.txt'  # Path for storing last modified time

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

def get_document_metadata(service):
    # Get the metadata for the document
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    last_modified_time = doc['revisionId']  # Alternative: use metadata like 'lastModifyingUser'
    return last_modified_time

def download_document(creds):
    # Use Google Drive API to download the document
    drive_service = build('drive', 'v3', credentials=creds)  # Pass creds directly to the Drive API
    request = drive_service.files().export_media(fileId=DOCUMENT_ID, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    
    # Execute the request to get the file's content
    response = request.execute()  # This gets the content of the file
    
    with open(LOCAL_FILE_PATH, 'wb') as file:
        file.write(response)  # Write the response content to the file

def main():
    # Authenticate with Google Docs API
    creds = authenticate_google_docs_api()
    service = build('docs', 'v1', credentials=creds)

    # Ensure the directory exists
    if not os.path.exists('../docs'):
        os.makedirs('../docs')

    # Get document metadata to check if it has been modified
    last_modified_time = get_document_metadata(service)

    # Load the last known state (e.g., last modified time)
    if os.path.exists(last_modified_file):
        with open(last_modified_file, 'r') as f:
            last_known_modified_time = f.read().strip()
    else:
        last_known_modified_time = None

    # If the document has been modified, download and replace it locally
    if last_modified_time != last_known_modified_time:
        print("Document has been modified, downloading updated version...")
        download_document(creds)  # Pass creds instead of service
        # Update the last known modified time
        with open(last_modified_file, 'w') as f:
            f.write(last_modified_time)
        # Optionally: Git commit the updated file
        os.system(f'git add {LOCAL_FILE_PATH}')
        os.system(f'git commit -m "Updated document to latest version"')
        print("Document updated and committed to Git.")
    else:
        print("No changes detected in the document.")

if __name__ == '__main__':
    main()
