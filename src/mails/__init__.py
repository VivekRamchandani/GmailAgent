import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# SCOPES = ["https://www.googleapis.com/auth/gmail.compose", "https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.labels"]
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def __get_creds():
    """
    Check Credentials
    """

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("creds/token.json"):
        creds = Credentials.from_authorized_user_file("creds/token.json")
        scopes_match = creds.has_scopes(SCOPES)
    # If there are no (valid) credentials available, let the user login.
    if not creds or not creds.valid or not scopes_match:
        # If creds expired refresh creds if we have refresh_token
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("creds/credentials.json", SCOPES)
            # Generate token    
            creds = flow.run_local_server(port=0)
        
        with open("creds/token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def __create_service():
    service = build("gmail", "v1", credentials=__get_creds())
    def service_getter():
        return service
    
    return service_getter

get_service = __create_service()
