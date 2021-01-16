import smtplib
from email.mime.text import MIMEText
from email.header import Header

IMPLEMENTED_EMAILS = {
    # 'google',
    # 'yahoo',
    # 'hotmail',
    'live': {'host': 'smtp.office365.com', 'port': 587}
}


class EmailSender:

    def __init__(self, adress, password):

        self.email_provider = adress.split('@')[1].split('.')[0]

        if self.email_provider in IMPLEMENTED_EMAILS.keys():
            self.adress = adress
            self.password = password

        else:
            raise NotImplementedError('Not implemented email yet')

    def send_email(self, receiver, mail_title, mail_content):
        #login
        mailserver = smtplib.SMTP(**(IMPLEMENTED_EMAILS[self.email_provider]))
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login(self.adress, self.password)
        #message
        msg = MIMEText(mail_content, "plain", 'utf-8')
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = self.adress
        msg["To"] = receiver
        #send
        mailserver.sendmail(self.adress, receiver, msg.as_string())
        mailserver.quit()
        print('E-mails successfully sent!')



