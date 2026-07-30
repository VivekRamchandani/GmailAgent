import os.path

from google.auth.transport.requests import Request
from googleapiclient.discovery import Resource
from email.message import EmailMessage
from . import get_service
from .messages import Draft, MessageInfo

import base64
import json

from typing import Literal

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

        # Encode Message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

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

    def list_labels(self) -> list[dict]:
        """List all Labels.

        Returns:
            list[dict]: list of labels
        """

        result = (
            self.service.users()
            .labels()
            .list(userId="me")
            .execute()
        )

        return result["labels"]


    def create_label(
        self, 
        name: str, 
        labelVisibility: Literal["labelShow", "labelShowIfUnread", "labelHide"], 
        messageListVisibility: Literal["show", "hide"]
    ) -> dict:
        """Create a new label

        Args:
            name (str): name of the label
            labelVisibility (Literal): Any one of the values "labelShow", "labelShowIfUnread" or "labelHide".
                For setting visibility of label in Gmail web interface.
            messageListVisibility (Literal): Either "show" or "hide".
                Whether to show messages with this label in the message list in the Gmail web interface.

        Returns:
            dict: Response of the request
        """
        label = {
            "labelListVisibility": labelVisibility,
            "messageListVisibility": messageListVisibility,
            "name": name
        }

        result = (
            self.service.users()
            .labels()
            .create(userId="me", body=label)
            .execute()
        )

        return result

    def delete_label(self, labelId: str):
        """Delete a label
        
        Args:
            labelId (str): Label Id for deleting
        """

        (
            self.service.users()
            .labels()
            .delete(userId="me", id=labelId)
            .execute()
        )


class MessageService():
    """Manage your Gmail Messages
    """

    def __init__(self):
        self.service = get_service()

    def list_messages(self, maxResults: int = 10, labelIds: list | None = None) -> list[MessageInfo]:
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
        if not result.get("messages", None):
            return []
        return [MessageInfo.from_dict(message) for message in result["messages"]]

    def send_message(
        self, 
        to_: str, 
        subject: str, 
        content: str, 
        addLabels: list[str] | None = None,
        showInInbox: bool = False
    ) -> MessageInfo:
        """Send Message

        Args:
            to_ (str): email address of reciever
            subject (str): Subject of mail
            content (str): Content of mail
            addLabels (list[str]): list of Label Ids to add
            showInInbox (bool): show message in inbox
            
        Return:
            MessageInfo: Returns sent message info 
        """
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

        # Modify Message
        modify = {}

        if addLabels:
            modify["addLabelIds"] = addLabels
        if not showInInbox:
            modify["removeLabelIds"] = ["INBOX"]
        
        if modify:
            sent_message = (
                get_service().users()
                .messages()
                .modify(userId="me", id=sent_message["id"], body=modify)
                .execute()
            )
    
        return MessageInfo.from_dict(sent_message)
