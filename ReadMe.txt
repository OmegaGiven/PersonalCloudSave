
In order to Setup automatic uploads to a google drive you will need to setup a google drive api link follow the following steps to do that:
Step 1: Set Up Google Drive API
    1. Go to https://console.cloud.google.com/ and log in.
    2. Create a New Project Click "Create Project" → Name it (e.g., "Game Save Backup").
    3. Enable Google Drive API
    4. Go to API & Services > Library
    5. Search for Google Drive API and enable it.
Step 2: Set Up Authentication
    1. Go to Credentials
    2. Click "Create Credentials" → Select OAuth Client ID
    3. Configure a consent screen (if prompted)
    4. Choose Desktop App as the application type.
    5. Download JSON Credentials
    6. Once created, download the client_secrets.json file.
    7. Place it in the same directory as your Python script.