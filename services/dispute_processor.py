from services import ocr_processor
import requests
import base64
import json
import os

def dispute_fun():
    #create response message templates
    path = "resources/dispute"
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.json' in file:
                files.append(os.path.join(r, file))
    for f in files:
        with open(f, 'r') as f:
            datastore = json.load(f)
        if datastore['attachment'] == "":
            #no attachment response
            outFile = 'resources/mail_template/{}_detail.json'.format(datastore['id'])
            f = open(outFile,'w+')
            mess = '''
            Please send the scaned copy of dispute mail for further processing

            Regards,
            EASE BANK
                    '''
            val = {
                    "id":datastore['id'],
                    "user_message":datastore['message'],
                    "Rmessage":mess,
                    "to":datastore['fro'],
                    "fro":datastore['to'],
                    "subject":datastore['subject'],
                    "date":datastore['date'],
                    "attachment":datastore['attachment']
                }
            f.write(json.dumps(val))
            f.close()
        else:
            ocr_data = ocr_processor.ocr_request(datastore['attachment'])
            print(ocr_data["OCRDetection"])
            if(str(ocr_data["OCRDetection"]) == "Success" and str(ocr_data["FormType"])== "DisputeForm"):
                #Generate the Service now ticket
                short = ocr_data["FieldsIdentified"]["CustomerName"]+" Issue : "+ocr_data["FormType"]
                description = " Date : "+ocr_data["FieldsIdentified"]["Date"]+"..CreditCardNo : "+ocr_data["FieldsIdentified"]["CreditCardNo"]+"..Details : Transaction Date ->"+ocr_data["FieldsIdentified"]["DisputeDetails"][0]["TransactionDate"]+", Merchant Name->"+ocr_data["FieldsIdentified"]["DisputeDetails"][0]["MerchantName"]+", TransactionAmount->"+ocr_data["FieldsIdentified"]["DisputeDetails"][0]["TransactionAmount"]+", Reason : "+ocr_data["FieldsIdentified"]["DisputeDetails"][0]["DisputeReason"]
                api_URL = ' https://dev77381.service-now.com/api/now/table/incident'
                payload = {
                    "caller_id": "Rick Berzle",
                    "short_description":short,
                    "description":description,
                    "category":"Software"
                         }
                usrPass = "admin:Test1234"
                b64Val = base64.b64encode(usrPass.encode("utf-8")).decode("utf-8")
                response=requests.post(api_URL,headers={"Content-Type":"application/json","Authorization": "Basic %s" % b64Val},data=json.dumps(payload))
                print(response.text)
                response = response.json()                
                #attachment response
                outFile = 'resources/mail_template/{}_detail.json'.format(datastore['id'])
                f = open(outFile,'w+')
                m = "Query Number : "+str((response['result']['number']))
                mess = '''
                Your dispute query is raised. please save the query number for further communication.

                Regards,
                EASE BANK
                    '''
                val = {
                        "id":datastore['id'],
                        "user_message":datastore['message'],
                        "Rmessage":m+mess,
                        "to":datastore['fro'],
                        "fro":datastore['to'],
                        "subject":datastore['subject'],
                        "date":datastore['date'],
                        "attachment":datastore['attachment']
                    }
                f.write(json.dumps(val))
                f.close()
            else:
                #attachment response
                outFile = 'resources/mail_template/{}_detail.json'.format(datastore['id'])
                f = open(outFile,'w+')
                mess = '''
                There is some problem with your dispute form. Please refill and send the form again

                Regards,
                EASE BANK
                    '''
                val = {
                        "id":datastore['id'],
                        "user_message":datastore['message'],
                        "Rmessage":mess,
                        "to":datastore['fro'],
                        "fro":datastore['to'],
                        "subject":datastore['subject'],
                        "date":datastore['date'],
                        "attachment":datastore['attachment']
                    }
                f.write(json.dumps(val))
                f.close()




