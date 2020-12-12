import smtplib, ssl

port = 465
password = input("Password: ")
sender_email = "shawn@furg.us"
receiver_email = "shawn@furgason.com"
message = """\
Subject: Hi there

This message is sent from Python."""

#Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL("mail.furg.us", port, context=context) as server:
    server.login("shawn@furg.us",password)
    server.sendmail(sender_email,receiver_email,message)
