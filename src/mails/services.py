from googleapiclient.discovery import Resource
from email.message import EmailMessage
from . import get_service
from .messages import Draft, MessageInfo

import base64
from pathlib import Path
import mimetypes

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
        attachments: list[str] = [],
        addLabels: list[str] = [],
        addHeaders: dict[str, str] = {},
        threadId: str | None = None, 
        showInInbox: bool = False
    ) -> MessageInfo:
        """Send Message

        Args:
            to_ (str): email address of reciever
            subject (str): Subject of mail
            content (str): Content of mail
            attachments (list[str]): List of path to files you want to attach to the mail.
            addLabels (list[str]): list of Label Ids to add
            addHeaders (dict[str, str]): add headers to email message
            threadId (str | None): send message to a particular thread
            showInInbox (bool): show message in inbox
            
        Returns:
            MessageInfo: Returns sent message info

        Raises:
            FileNotFoundError: If incorrect attachment path is passed
            Execption: When maximum total attachment size is execeeded
        """
        message = EmailMessage()
        message.set_content(content)
    
        message["To"] = to_
        message["From"] = "me"
        message["Subject"] = subject

        # Attachment Limit set to 18 MB
        # 'cause base64 encoding has 33% overhead
        attachmentLimit = 18874368

        # Adding Attachments
        if attachments:
            for attachment in attachments:
                filepath = Path(attachment)
                if not filepath.exists():
                    raise FileNotFoundError(f"{filepath} doesn't exists.")                  # TODO: Need to raise error here

                filesize = filepath.stat().st_size
                attachmentLimit -= filesize

                if attachmentLimit < 0:
                    raise Exception("Attachment Limit of 18 MB exceeded.")                  # TODO: Need to raise error here

                with open(filepath, "rb") as file:
                    filename = filepath.name
                    file_content = file.read()
                    type_subtype, _ = mimetypes.guess_type(filepath)
                    if not type_subtype:
                        type_subtype = "application/octet-stream"
                    main_type, sub_type = type_subtype.split("/")

                message.add_attachment(file_content, main_type, sub_type, filename=filename)

        # Adding Headers
        if addHeaders:
            for header, value in addHeaders:
                message.add_header(header, value)
    
        # Encode message 
        encoded_messsage = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
        created_message = {"raw": encoded_messsage}

        if threadId:
            created_message["threadId"] = threadId
    
        sent_message = (
            self.service.users()
            .messages()
            .send(userId="me", body=created_message)
            .execute()
        )

        # Modify Message
        modify = {}

        if addLabels:
            modify["addLabels"] = addLabels
        if not showInInbox:
            modify["removeLabels"] = ["INBOX"]
        
        if modify:
            modify["messageId"] = sent_message["id"]
            return self.modify_message(**modify)
    
        return MessageInfo.from_dict(sent_message)

    def reply_to(self, messageId: str, content: str, attachments: list[str] = []) -> MessageInfo:
        """Reply to an Email Message
        
        Args:
            messageId (str): messageId of email message you want to reply to.
            content (str): Content of the email

        Returns:
            MessageInfo: info of sent message

        Raises:
            Execption: Message id doesn't exists
        """

        msg = MessageInfo(messageId, "")

        try:
            message = msg.get_full_message()
        except:
            raise Exception(f"message id '{msg.id}' doesn't exists.")

        references = message.payload.rawHeaders.get("References", "")
        in_reply_to = message.payload.rawHeaders["Message-ID"]
        if references:
            references += " "
        references += in_reply_to
    
        to_ = message.payload.from_
        subject = message.payload.subject
        threadId = message.threadId

        headers = {
            "References": references,
            "In-Reply-To": in_reply_to
        }

        return self.send_message(to_, subject, content, attachments, threadId=threadId, addHeaders=headers)

    def modify_message(self, messageId: str, addLabels: list[str], removeLabels: list[str]) -> MessageInfo:
        """Modify Email
        
        Args:
            messageId (str): message Id
            addLabels (list[str]): labels to add to the email
            removeLabels (list[str]): labels to remove from email
        
        Returns:
            MessageInfo: Returns sent message info
        """

        modify = {}
        
        if addLabels:
            modify["addLabelIds"] = addLabels
        if removeLabels:
            modify["removeLabelIds"] = removeLabels
        
        if modify:
            sent_message = (
                self.service.users()
                .messages()
                .modify(userId="me", id=messageId, body=modify)
                .execute()
            )

        return MessageInfo.from_dict(sent_message)