## ***mails*** Module

For simple management of **mails**, **drafts** and **labels**

## Basic Documentation

The three main classes are `MessageService()`, `DraftService()` and `LabelService()` for managing messages, drafts and labels.

### Managing Messages

Following features are provided in `MessageService()` class:

1. Listing Messages

    ```python
    message_service = MessageService()
    msgs = message_service.list_messages()
    for msg in msgs:
        print(msg)
    ```

2. Sending Message

    ```python
    to = "xyz@gmail.com"
    subject = "Automated Mail"
    content = "This is an automated mail"
    sent_msg = message_service.send_message(to, subject, content)

    print(sent_msg.get_full_message())
    ```
    The `send_message()` only returns the message info (`MessageInfo` object) of the sent message. To see the full message just call `get_full_message()` of `MessageInfo` object to get the full message (`Message` object)


### Managing Labels

Following things can be done using `LabelService()` class

1. Listing Labels

    ```python
    label_service = LabelService()
    labels = label_service.list_labels()
    print(labels)
    ```

2. Creating Labels

    ```python
    label_name = "DUMMY"
    label_visibility = "labelShow"
    message_list_visibility = "show"
    created_label = label_service.create_label(label_name, label_visibility, message_list_visibility)
    print(created_label)
    ```

To send message/mail to with your created label simply use `addLabels` argument in `send_message()` method.


### Managing Drafts

Following things can be done using `DraftService()` class

1. Listing Drafts

    ```python
    draft_service = DraftService()
    max_results = 5
    drafts = draft_service.list_drafts(5)
    for draft in drafts:
        print(draft)
    ```

2. Creating Draft

    ```python
    to = "xyz@gmail.com"
    subject = "Automated Draft"
    content = "This is automated Draft."

    draft = draft_service.create_draft(to, subject, content)
    print(draft)
    ```
