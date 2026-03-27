import os.path

from google.auth.transport.requests import Request
from googleapiclient.discovery import Resource
from email.message import EmailMessage
from . import get_service
from .messages import Draft, MessageInfo

import base64
import json

class DraftManager():
    """Class to Manage Gmail Drafts.
    """
    def __init__(self):
        self.service: Resource = get_service()

    def create_draft(self, content: str):
        """Create Draft

        Args:
            content (str): content to add into Draft
        """

        # Create Email Message
        message = EmailMessage()
        
        # Add Content
        message.set_content(content)

        # Message Information
        message["To"] = "vivekramchandanihvj@gmail.com"
        message["From"] = "vivekramchandanihvj@gmail.com"
        message["Subject"] = "Automated Draft"

        # print(message.as_string())

        # Encode Message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        # print(encoded_message)

        create_message = {"message": {"raw": encoded_message} }

        draft = (
            self.service.users()
            .drafts()
            .create(userId="me", body=create_message)
            .execute()
        )

        print(type(draft))
        print(draft)

    def list_drafts(self, max: int | None = None) -> list[Draft]:
        """List all the Drafts

        Args:
            max (int): Max number of results to return.

        Returns:
            drafts (list[Draft]): List of Drafts
        """

        kwargs = {
            "userId": "me",
        }
        if max:
            kwargs["maxResults"] = max

        results = (
            self.service.users()
            .drafts()
            .list(**kwargs)
            .execute()
        )

        drafts = [Draft.from_dict(draft) for draft in results["drafts"]]

        return drafts

class LabelManager():
    """Manage your Gmail Labels
    """
    
    def __init__(self):
        self.service = get_service()

    def list_labels(self):
        """List all Labels.
        """

        result = (
            self.service.users()
            .labels()
            .list(userId="me")
            .execute()
        )

        return result["labels"]

class MessageManager():
    """Manage your Gmail Messages
    """

    def __init__(self):
        self.service = get_service()

    def list_messages(self, maxResults: int, labelIds: list):
        """Fetch Messages from Gmail
        """

        result = (
            self.service.users()
            .messages()
            .list(userId="me", labelIds=labelIds, maxResults=maxResults)
            .execute()
        )

        return result["messages"]
    
    def get_message(self, messageId: str):
        """Get full detail of a Message
        """

        result = (
            self.service.users()
            .messages()
            .get(userId="me", id=messageId, format="full")
            .execute()
        )

        return result