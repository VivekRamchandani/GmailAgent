import os.path

from google.auth.transport.requests import Request
from googleapiclient.discovery import Resource
from email.message import EmailMessage
from . import get_service
from .messages import Draft, MessageInfo

import base64
import json

class DraftService():
    """Class to Manage Gmail Drafts.
    """
    def __init__(self):
        self.service: Resource = get_service()

    def create_draft(self, to_: str, subject: str, content: str) -> Draft:
        """Create Draft

        Args:
            to_ (str): Send to
            subject (str): subject of draft
            content (str): content to add into Draft
        """

        # Create Email Message
        message = EmailMessage()
        
        # Add Content
        message.set_content(content)

        # Message Information
        message["To"] = to_
        message["From"] = "me"
        message["Subject"] = subject

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

        return Draft.from_dict(draft)

    def list_drafts(self, max: int | None = None) -> list[Draft]:
        """List all the Drafts

        Args:
            max (int): Max number of results to return.

        Returns:
            drafts (list[Draft]): List of Drafts object
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

class LabelService():
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

class MessageService():
    """Manage your Gmail Messages
    """

    def __init__(self):
        self.service = get_service()

    def list_messages(self, maxResults: int = 100, labelIds: list | None = None) -> list[MessageInfo]:
        """Fetch Messages from Gmail

        Args:
            maxResults (int): Max number of messages to return
            labelIds (list): Only returns messages that match the labelIds passed

        
        Returns:
            list: Return list of `MessageInfo`.
        """

        kwargs = {
            "userId": "me",
            "maxResults": maxResults
        }
        if labelIds:
            kwargs["labelIds"] = labelIds

        result = (
            self.service.users()
            .messages()
            .list(**kwargs)
            .execute()
        )

        return [MessageInfo.from_dict(message) for message in result["messages"]]

    def send_message(self, to_: str, subject: str, content: str) -> MessageInfo:
        message = EmailMessage()
        message.set_content(content)
    
        message["To"] = to_
        message["From"] = "me"
        message["Subject"] = subject
    
    
        # Encode message 
        encoded_messsage = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
        created_message = {"raw": encoded_messsage}
    
        sent_message = (
            get_service().users()
            .messages()
            .send(userId="me", body=created_message)
            .execute()
        )
    
        return MessageInfo.from_dict(sent_message)
