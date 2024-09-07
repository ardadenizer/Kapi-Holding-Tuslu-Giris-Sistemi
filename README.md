# Project Description

Coskun Tasdemir'in  superpeer platformu ustunde  duzenledigi serinin proje reposu.

# Python Requirements
## Setting Up Python Environment
To run the script, you need to have Python 3.x installed and set up in your environment. You'll also need to install the necessary Python packages.

Install the Python dependencies from the requirements.txt file by running:
`pip install -r requirements.txt`

## What the Script Does
The **update_docs_local.py** script automates the following tasks:

 1. Authentication:

The script uses OAuth2 to authenticate with Google APIs (Google Docs API and Google Drive API).
It uses **credentials.json** for authentication details and stores tokens in token.pickle to avoid asking for authentication every time the script runs.

 2. Checking for Document Updates:

The script checks the last modified time (revisionId) of each document defined in the DOCS dictionary.
It compares this time with a locally stored last_modified.txt file for each document.

 3. Downloading Updated Documents:

If a document has been modified since the last check, the script downloads it as a .docx file and saves it in the **docs/** folder.

 4. Git Commit:

After downloading the updated document, the script adds and commits the file to your Git repository.

## How to Run the Script
### Prerequisites:
#### Google Cloud Console Setup:
1. Create a project in Google Cloud Console.

2. Enable the Google Docs API and Google Drive API.

3. Create OAuth2 credentials and download the **credentials.json** file.

#### Place the Credentials File:
Save the **credentials.json** file in the **scripts/** folder or set up an environment variable **(GOOGLE_CREDENTIALS_PATH)** to point to its location.

Running the Script
1. Initial Authentication:

The first time you run the script, it will prompt you to log in to your Google account and authorize access to the documents. After successful authentication, a **token.pickle** file will be created, which stores OAuth2 tokens for future access.

2. Run the Script:

To run the script, use the following command: `python ./scripts/update_docs_local.py`

The script will:

* Authenticate with Google APIs.
* Check each document in the DOCS dictionary.
* Download any documents that have been updated since the last check.
* Commit the updated documents to your Git repository.

## Adding New Documents
1. To add a new Google Doc for tracking:

Add a new entry to the **DOCS** dictionary in the **update_docs_local.py** script with the document name as the key and the document ID as the value.

```python
DOCS = {
    'functional_requirements': '1NxX7krtwGDKubcgMhywKqDutGe2N-S4RxEhr5U7UBcQ',
    'system_block_diagram': '1_jM4hqGpjIw_PULmp0QU2PRDqzd9vfIFmgAreEXpT6Y',
    'another_doc': '1ExampleDocIDforAnotherGoogleDoc'
}
```
2. Re-run the script to start tracking and downloading the new document.

## Important Notes
* Security:
Never share your **credentials.json** file or **token.pickle** file publicly. These contain sensitive credentials that can be used to access your Google account.
Add these files to your **.gitignore** to prevent accidentally committing them to Git.
* Rate Limits:
Google APIs have usage limits. If you run the script too frequently, you may hit Google API rate limits. You can monitor your API usage in the [Google Cloud Console](https://console.cloud.google.com).
