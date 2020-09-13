#!/usr/bin/env python3

import smtplib
from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def sendReportEmail(subject, message):
    mailContent = message

    #The mail addresses and password
    senderAddress = 'gso.nguyenkhai@gmail.com'
    senderPass = 'quockhai@gso'
    receiverAddress = 'quockhai.vn@gmail.com'

    # now = datetime.now()
    # subject = '[Ps] ' + str(itemNumber) + ' items (' + now.strftime("%Hh%M %d/%m") + ')'
    # if message.find('[404]') >= 0:
    #     subject = '[Ps] 404! report at ' + now.strftime("%Hh%M %d/%m")

    #Setup the MIME
    message = MIMEMultipart()
    message['From'] = senderAddress
    message['To'] = receiverAddress
    message['Subject'] = subject
    #The body and the attachments for the mail
    message.attach(MIMEText(mailContent, 'plain'))

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(senderAddress, senderPass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(senderAddress, receiverAddress, text)
    session.quit()
    print('Mail Sent.')