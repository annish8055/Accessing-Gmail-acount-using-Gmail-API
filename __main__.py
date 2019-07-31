from services import mail_tiaging
from services import ocr_processor
from services import dispute_processor
from services import send_mail

if __name__ == "__main__":
    mail_tiaging.read_mail()
    dispute_processor.dispute_fun()
    #result = ocr_processor.ocr_request()
    send_mail.send()

