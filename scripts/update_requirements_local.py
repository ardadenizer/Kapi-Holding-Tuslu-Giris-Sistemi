import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

# If modifying these SCOPES, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

# The ID of the Google Docs document you want to check
DOCUMENT_ID = '1NxX7krtwGDKubcgMhywKqDutGe2N-S4RxEhr5U7UBcQ'
LOCAL_FILE_PATH = './functional_requirements.docx'  # or other format

def authenticate_google_docs_api():
    creds = None
    # Load credentials from token.pickle if available
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid credentials, log in using OAuth2
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_document_metadata(service):
    # Get the metadata for the document
    doc = service.documents().get(documentId=DOCUMENT_ID).execute()
    last_modified_time = doc['revisionId']  # Alternative: use metadata like 'lastModifyingUser'
    return last_modified_time

def download_document(service):
    # Use Google Drive API to download the document
    drive_service = build('drive', 'v3', credentials=service._credentials)
    request = drive_service.files().export_media(fileId=DOCUMENT_ID, mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    with open(LOCAL_FILE_PATH, 'wb') as file:
        file.write(request.content)

def main():
    # Authenticate with Google Docs API
    creds = authenticate_google_docs_api()
    service = build('docs', 'v1', credentials=creds)

    # Get document metadata to check if it has been modified
    last_modified_time = get_document_metadata(service)

    # Load the last known state (e.g., last modified time)
    if os.path.exists('last_modified.txt'):
        with open('last_modified.txt', 'r') as f:
            last_known_modified_time = f.read().strip()
    else:
        last_known_modified_time = None

    # If the document has been modified, download and replace it locally
    if last_modified_time != last_known_modified_time:
        print("Document has been modified, downloading updated version...")
        download_document(service)
        # Update the last known modified time
        with open('last_modified.txt', 'w') as f:
            f.write(last_modified_time)
        # Optionally: Git commit the updated file
        os.system(f'git add {LOCAL_FILE_PATH}')
        os.system(f'git commit -m "Updated document to latest version"')
        print("Document updated and committed to Git.")
    else:
        print("No changes detected in the document.")

if __name__ == '__main__':
    main()
