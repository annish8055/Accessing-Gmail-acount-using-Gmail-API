import requests
import os
import json

def ocr_request(file_path):
    path = 'resources/mail_attachments'
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.jpg' in file or '.png' in file:
                files.append(os.path.join(r, file))
    url = 'https://contactcenternodeapi.azurewebsites.net/ocrdisputeform'
    files = {'AttachmentName':file_path,'File': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    fin_res = json.loads(response.text)
    print(fin_res["OCRDetection"])
    #response = json.load(response)
    #response["Filename"]= file_path
    return fin_res