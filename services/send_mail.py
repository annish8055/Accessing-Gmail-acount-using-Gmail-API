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

'''
-----REFRESH TOKEN--------
https://developers.google.com/gmail/api/quickstart/python?pli=1&authuser=3
'''

# If modifying these scopes, delete the file token.pickle.
SCOPES = 'https://mail.google.com/'
return_mail=""

def send():
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
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    print(return_mail)
    path = "resources/mail_template"
    files = []
    with open("resources/mail_history/logs.json", "r+") as log:
            data = json.load(log)
    for r, d, f in os.walk(path):
        for file in f:
            if '.json' in file:
                files.append(os.path.join(r, file))
    for f in files:
        with open(f, 'r') as f:
            datastore = json.load(f)
        #Creating Log
        print(len(data["history"]))
        data["history"].append({
            "ID":datastore["id"],
            "Sender":datastore["to"],
            "Subject":datastore["subject"],
            "Message":datastore["user_message"],
            "Attachment":datastore["attachment"],
            "ResponseMessage":datastore["Rmessage"],
            "date":datastore["date"],
            "Status":"Sent"
        })   
        #Sending Mail
        message = MIMEText(datastore["Rmessage"])
        message['to'] = datastore["to"]
        message['from'] = datastore["fro"]
        message['subject'] = datastore["subject"]
        message = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}
        try:
            message = (service.users().messages().send(userId='me', body=message)
                .execute())
            print('Message Id: %s' % message['id'])
            #('resources/dispute/')
            #('resources/mail_attachments/')
        except Exception as e: print(e)
    log.close()
    log_fin = open("resources/mail_history/logs.json", "w+")
    log_fin.write(json.dumps(data))
    log_fin.close() 
    path = 'resources/other_mail'
    for r, d, f in os.walk(path):
        for file in f:
            os.remove(path+"/"+file)
    path = 'resources/dispute'
    for r, d, f in os.walk(path):
        for file in f:
            os.remove(path+"/"+file)
    path = 'resources/mail_attachments'
    for r, d, f in os.walk(path):
        for file in f:
            os.remove(path+"/"+file)
    path = 'resources/mail_template'
    for r, d, f in os.walk(path):
        for file in f:
            os.remove(path+"/"+file)