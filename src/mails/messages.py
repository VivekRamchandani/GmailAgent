from . import get_service
import base64

class MessageInfo():
    """This class represnts message basic info of Gmail Message"""
    
    def __init__(self, messageId, threadId):
        self.id = messageId
        self.threadId = threadId

    @staticmethod
    def from_dict(obj: dict):
        return MessageInfo(obj["id"], obj["threadId"])
    
    def get_full_message(self):
        service = get_service()

        msg = (
            service.users()
            .messages()
            .get(userId="me", id=self.id, format="full")
            .execute()
        )

        return Message.from_dict(msg)

class Draft():
    """This class represents a Draft in Gmail"""

    def __init__(self, draftId, messageInfo: MessageInfo):
        self.id = draftId
        self.messageInfo = messageInfo
    
    @staticmethod
    def from_dict(obj: dict):
        return Draft(obj["id"], MessageInfo.from_dict(obj["message"]))


class Message():
    """
    """

    def __init__(self, messageId, threadId, labelIds, payload: dict):
        self.id = messageId
        self.threadId = threadId
        self.labelIds = labelIds
        self.payload = self.Payload.from_dict(payload)

    def get_content(self):
        return self.payload.get_content()

    def get_attachment(self, attachmentId) -> bytes:
        service = get_service()
        result = (
            service.users()
            .messages()
            .attachments()
            .get(userId="me", messageId=self.id, id=attachmentId)
            .execute() 
        )

        data = result["data"]
        return base64.urlsafe_b64decode(data)

    @staticmethod
    def from_dict(obj: dict):
        return Message(obj["id"], obj["threadId"], obj["labelIds"], obj["payload"])

    class Payload():
        """Class for Pyaload of Message
        """

        def __init__(self, mimeType: str, headers: list, body: dict, parts: list | None = None):
            """Initialize Payload Class

            Args:
                mimeType (str): Mime type of the payload
                headers (list): List of headers in the message
                body (dict): Main body of the Payload
                parts (list): Requried when main beody of Payload is empty
            
            Raises:
                ValueError: When body size is 0 and parts is None or empty.
            """
            self.partId = ""
            self.mimeType = mimeType
            self.rawHeaders = {header["name"]: header["value"] for header in headers}
            self.to_ = self.rawHeaders["To"]
            self.from_ = self.rawHeaders["From"]
            self.subject = self.rawHeaders["Subject"]
            self.dateStr = self.rawHeaders["Date"]
            self.content = None
            self.attachments = []
            self.rawParts = {}

            if body["size"]:
                self.content = body.get("data", None)
                if body.get("attachmentId", None):
                    attachment = {
                        "attachmentId": body["attachmentId"],
                        "filename": body["filename"],
                        "size": body["size"]
                    }
                    self.attachments.append(attachment)
            elif parts:
                # Searching for content and attachtments in parts.
                queue = [part for part in parts]    # Using BFS technique
                for part in queue:
                    rawPart = { 
                        "partId": part["partId"], 
                        "mimeType": part["mimeType"] 
                    } 
                    if part["mimeType"] == "multipart/alternative":
                        queue.extend(part["parts"])
                    elif part["mimeType"] == "text/plain":
                        self.content = part["body"]["data"]
                        rawPart["body"] = part["body"]
                    elif part["body"].get("attachmentId", None):
                        rawPart["body"] = part["body"]
                        attachment = {
                            "attachmentId": part["body"]["attachmentId"],
                            "filename": part["filename"],
                            "size": part["body"]["size"]
                        }
                        self.attachments.append(attachment)                  

                    self.rawParts[part["partId"]] = rawPart
            else:
                raise ValueError("Body size is 0 and parts is None or empty")

        def get_content(self):
            return base64.urlsafe_b64decode(self.content).decode()
        
        def list_parts(self):
            return self.rawParts.keys()

        def get_part(self, partId: str):
            if partId not in self.rawParts.keys():
                raise KeyError(f"{partId} not found.")
            return self.rawParts[partId]

        @staticmethod
        def from_dict(obj: dict):
            if obj["mimeType"] == "multipart/alternative":
                return Message.Payload(obj["mimeType"], obj["headers"], obj["body"], obj["parts"])
            else:
                return Message.Payload(obj["mimeType"], obj["headers"], obj["body"])