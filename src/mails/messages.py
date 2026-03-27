from . import get_service

class MessageInfo():
    """This class represnts message basic info of Gmail Message"""
    
    def __init__(self, id, threadId):
        self.id = id
        self.threadId = threadId

    @staticmethod
    def from_dict(obj: dict):
        return MessageInfo(obj["id"], obj["threadId"])
    
    def get_full_message(self):
        service = get_service()

        result = (
            service.users()
            .messages()
            .get(userId="me", id=self.id, format="full")
            .execute()
        )

class Draft():
    """This class represents a Draft in Gmail"""

    def __init__(self, id, messageInfo: MessageInfo):
        self.id = id
        self.messageInfo = messageInfo
    
    @staticmethod
    def from_dict(obj: dict):
        return Draft(obj["id"], MessageInfo.from_dict(obj["message"]))