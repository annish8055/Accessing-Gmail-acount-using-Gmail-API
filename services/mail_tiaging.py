from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import shutil
import requests
from email.mime.text import MIMEText
import smtplib
import json

SCOPES = 'https://mail.google.com/'
return_mail=""

def read_mail():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    results = service.users().messages().list(userId='me',labelIds = ['INBOX','UNREAD']).execute()
    messages = results.get('messages', [])
    if not messages:
        print("No messages found.")
    else:
        print("Message snippets:")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            mesId = ""
            to = ""
            fro = ""
            subject = ""
            date = ""
            mess1 = msg['snippet']
            id = msg['id']
            for data in msg['payload']['headers']: 
                if data['name'] == "Subject":
                    subject = data['value']
                    break
            for data in msg['payload']['headers']: 
                if data['name'] == "Date":
                    date = data['value']
                    break
            for data in msg['payload']['headers']: 
                if data['name'] == "Message-ID":
                    mesId = data['value']
                    break
            for data in msg['payload']['headers']: 
                if data['name'] == "From":
                    fro = data['value']
                    break
            print("---------Message ID---------",mesId)
            #print(msg)
            #-----Modify mail from unread to read--------------------
            mes = {
                  "removeLabelIds": [
                      "UNREAD"
                    ],
                    "addLabelIds": [
                        "INBOX"
                    ]
                }
            mess = service.users().messages().modify(userId='me', id=msg['id'], body=mes).execute()
            label_ids = mess['labelIds']
            print('Message ID: %s - With Label IDs %s' % (msg['id'], label_ids))
            #----------------End---------------
            if("dispute" in str(subject).lower()):
                try:
                    attachment = service.users().messages().attachments().get(
                       userId='me', messageId=mesId, id=msg['payload']['parts'][1]['body']['attachmentId']
                       ).execute()
                    extension = msg['payload']['parts'][1]['filename'].split('.')[1]
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    path = ""
                    if extension == 'pdf':
                        path = 'resources/mail_attachments/{}_metadata.pdf'.formate(id)
                        with open(path, 'wb') as f:
                            f.write(file_data)
                    elif extension == 'png':
                        path = 'resources/mail_attachments/{}_img.png'.format(id)
                        with open(path, 'wb') as f:
                            f.write(file_data)
                    elif extension == 'jpg':
                        path = 'resources/mail_attachments/{}_img.jpg'.format(id)
                        with open(path.id, 'wb') as f:
                            f.write(file_data)
                    outFile = 'resources/dispute/{}_detail.json'.format(id)
                    f = open(outFile,'w+')
                    val = {
                        "id":id,
                        "message":mess1,
                        "to":"JohnRussellPro@gmail.com",
                        "fro":fro,
                        "subject":subject,
                        "date":date,
                        "attachment":path
                    }
                    f.write(json.dumps(val))
                    f.close()
                except:
                    # No attachment Flow
                    outFile = 'resources/dispute/{}_detail.json'.format(id)
                    f = open(outFile,'w+')
                    val = {
                        "id":id,
                        "message":"",
                        "to":"JohnRussellPro@gmail.com",
                        "fro":fro,
                        "subject":subject,
                        "date":date,
                        "attachment":""
                    }
                    f.write(json.dumps(val))
                    f.close()
            else:
                # other Folder
                outFile = 'resources/other_mail/{}_detail.json'.format(id)
                f = open(outFile,'w+')
                val = {
                        "id":id,
                        "message":"",
                        "to":"JohnRussellPro@gmail.com",
                        "fro":fro,
                        "subject":subject,
                        "date":date,
                        "attachment":""
                    }
                f.write(json.dumps(val))
                f.close()
            