from django.core.mail import EmailMessage  
import re
import threading
import phonenumbers
from django.template.loader import render_to_string
from rest_framework.exceptions import ValidationError
from decouple import config
from twilio.rest import Client

email_regex = re.compile('[^@ \t\r\n]+@[^@ \t\r\n]+\.[^@ \t\r\n]+')
phone_regex = re.compile('^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$')

def check_email_or_phone(email_or_phone):
    phone_number = phonenumbers.parse(email_or_phone)

    if re.fullmatch(email_regex, email_or_phone):
        email_or_phone = "Email"
    elif phonenumbers.is_valid_number(phone_number):
        email_or_phone = "Phone"
    else:
        data = {
            "success": False,
            "message": "Email yoki Tel raqam kiriting"
        }

        raise ValidationError(data)
    return email_or_phone

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

class Email:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['subject'],
            body=data['body'],
            to=[data['to_email']]
        )
        if data.get('content_type') == "html":
            email.content_subtype = 'html'
        EmailThread(email).start()

def send_email(email, code):
    html_content = render_to_string(
        'email/authentication/activate_account.html',
        {'code': code}
    )
    Email.send_email(
        {
            'subject': "Ro'yxatdan o'tish",
            "to_email": email,
            "body": html_content,
            "content_type": "html"
        }
    )

def send_phone_code(phone, code):
    account_sid = config('account_sid')
    auth_token = config('auth_token')
    client = Client(account_sid, auth_token)
    client.messages.create(
        body=f"Salom do'stim sizning tastiqlash kodingiz: {code}\n",
        from_="+998999441804",
        to=f"{phone}"
        
    )

