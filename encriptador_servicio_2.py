from googleapiclient.discovery import build
from google.oauth2 import service_account

# Your service account dictionary (as in your code)
SERVICE_ACCOUNT_FILE = {
   # Contenido .json credencial de api de google drive
}

SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = "1CJi8m_p2fjjA1HcyR8ThUZq7aJ_uCg8b"

# Now we use from_service_account_info to load the credentials directly from the dictionary
def authenticate():
    creds = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def upload_photo(file_path):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': "Demonstration",
        'parents': [PARENT_FOLDER_ID]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=file_path
    ).execute()

upload_photo("key.key")
