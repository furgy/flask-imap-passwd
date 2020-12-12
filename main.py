from flask import Flask, render_template, request, redirect, flash, abort, url_for
from wtforms import Form, PasswordField, HiddenField, BooleanField
from wtforms.validators import EqualTo, InputRequired
from datetime import datetime as dt
import imaplib
import os
from cryptography.fernet import Fernet
import smtplib, ssl
# import config_messages

class CredentialsForm(Form):
    token_id = HiddenField()
    username = HiddenField()
    resetPasswd = BooleanField()
    passwd = PasswordField('Password', [InputRequired(),EqualTo('passwd_validation', message="The passwords must match")],
        render_kw={"data-eye-class":"fa", "data-eye-open-class":"fa-eye",                                        "data-eye-close-class":"fa-eye-slash",
        "data-toggle":"password"})
    passwd_validation = PasswordField('Confirm Password',[InputRequired()],
        render_kw={"data-eye-class":"fa", "data-eye-open-class":"fa-eye",                                        "data-eye-close-class":"fa-eye-slash",
        "data-toggle":"password"})

app = Flask(__name__)
app.config['SECRET_KEY'] = 'akjtlwejaleijlaenlfnl'
SENDER_EMAIL_ADDR = os.environ.get('SENDER_EMAIL_ADDR')
SENDER_EMAIL_PASS = os.environ.get('SENDER_EMAIL_PASS')
EMAIL_SERVER_ADDR = os.environ.get('EMAIL_SERVER_ADDR')
EMAIL_DOMAIN = '@furgason.com'
EMAIL_VALIDATION_ADDR = "mail.ionos.com"
EMAIL_SERVER_PORT = 465
FLASK_ENV = os.environ.get('FLASK_ENV')

SET_EMAIL_PASSWORD_MSG="""\
From: Shawn Furgason <shawn@furgason.com>
Subject: furgason.com email account password status.

Hi [[recipient name]],
Thanks for setting your email account preferences to support the upcoming migration.

[[recipient preferences]]

At any time, up until I start the email migration,  you can use the link 
provided earlier to change your email account preferences.  It's important that you 
keep this information secure as it will allow anyone that has it change your 
preferences and/or retrieve your password.

Thanks again for your help.  You'll receive information shortly on when the 
email migration will take place and what you should expect.

If you have any questions in the meantime, feel free to drop me an email. 

Thanks,
Shawn"""

PREF_RESET="""\
Per your request, your password will be reset to faciliate the migration.
As soon as your password is reset, I will provide you an update how to to 
retrieve your new account password.  This new password will work for both 
your existing and new email accounts.

After the migration, it is recommended you change your password.  I will 
provide instructions on how to do this once the migration is complete."""

PREF_STORE="""\
Per your request, your password has been securely stored to facilitate
the migration.  

After the migration, it is recommended you change your password.  I will 
provide instructions on how to do this once the migration is complete."""

ENC_KEY = bytes(os.environ.get('ENC_KEY'),'utf-8')
if ENC_KEY is None:
    exit(1)

def send_email(recipient,message):
    #Create a secure SSL context

    if FLASK_ENV == "development":
        print(f"Recipient: {recipient}")
        print(f"Message:\n{message}")
        recipient = "shawn@furgason.com"
        
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(EMAIL_SERVER_ADDR, EMAIL_SERVER_PORT, context=context) as server:
        server.login(SENDER_EMAIL_ADDR,SENDER_EMAIL_PASS)
        server.sendmail(SENDER_EMAIL_ADDR,recipient,message)

def encrypt_string(enc_string):
    f = Fernet(ENC_KEY)
    return f.encrypt(enc_string.encode())

def decrypt_string(enc_string):
    enc_string = enc_string[2:][:-1]
    # print(f"String to decrypt: {enc_string}")
    f = Fernet(ENC_KEY)
    return f.decrypt(bytes(enc_string,'utf-8')).decode()

def store_password(token_id,passwd):
    with open('credentials.txt') as f:
        cred_file = f.read()

    datestamp = dt.now().strftime('%Y-%m-%d:%H:%M:%S')
    oF = open('credentials.txt', 'w') 
    for record in cred_file.split('\n'):
        items = record.split(';')
        password = " "
        datestamp = " "
        # print(items)
        if len(items) > 1:
            username = items[0]
            token = items[1]
            if len(items) > 2:
                password = items[2]
            if len(items) > 3:
                datestamp = items[3]
            # print(f"Do the tokens match? ({token}) vs ({token_id}) {token == token_id}")
            if token == token_id:
                password = passwd
                datestamp = dt.now().strftime('%Y-%m-%d:%H:%M:%S')
            oF.write(f"{username};{token};{password};{datestamp}\n")

    oF.close()

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return render_template('500.html'), 500

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))
    
@app.route('/')
def index():
    return "Hello World"

# @app.route('/faq.html')
@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/s/<template_name>')
def template(template_name):
    return render_template(f"{template_name}")

@app.route('/t')
@app.route('/t/<token_id>')
def get_token(token_id='n'):
    t = request.args.get('token_id') 
    r = request.args.get('resetPasswd')
    if t:
        token_id = t
    if token_id != "n":
        token_match = False
        with open('credentials.txt','r') as f:
            for line in f:
                # print(line)
                items = line.split(';')
                f_token = items[1].strip('\n')
                if token_id == f_token:
                    token_match = True
                    form = CredentialsForm()
                    user = items[0]
                    # print(f"Token match: {token_id}: {f_token}")

                    return render_template('passwd.html', token_id=token_id, form=form, user=user)
                    
        return render_template('invalid.html', token_id=token_id)
    else:
        token_id = request.args.get('token_id')
        if token_id:
            form = CredentialsForm()
            return render_template('passwd.html', token_id=token_id, form=form)
        return render_template('reqtoken.html')

@app.route('/getpasswd', methods=['GET','POST'])
def getpasswd():
    if request.method == 'POST':
        token_id = request.form.get('token_id')

        token_match = False
        validPasswd = False
        passwdNotSet = True
        password = ""
        # print(token_id)
        with open('credentials.txt','r') as f:
            for line in f:
                items = line.split(';')
                # print(items)
                f_token = items[1].strip('\n')
                if token_id == f_token:
                    token_match = True
                    password = items[2]
                    # print(f"Password is: {password}")
                    if password == " " or password == "<reset>":
                        validPasswd = False
                        if password == " ":
                            passwdNotSet = True
                        if password == "<reset>":
                            passwdNotSet = "<reset>"
                    else:
                        validPasswd = True
                        passwdNotSet = False
                        password = decrypt_string(password)
                    break

        return render_template('getpasswd.html', password=password, validPasswd=validPasswd, passwdNotSet=passwdNotSet)
    else:
        return render_template('gettoken.html')

@app.route('/confirmation', methods=['POST'])
def confirmation():
    form = CredentialsForm(request.form)
    if request.method == 'POST':
        user = form.username.data
        username = form.username.data
        token_id = form.token_id.data
        resetPasswd = form.resetPasswd.data
        print(resetPasswd)
        if resetPasswd == True:
            store_password(token_id,"<reset>")
            msg = SET_EMAIL_PASSWORD_MSG.replace("[[recipient name]]",user)
            msg = msg.replace("[[recipient preferences]]",PREF_RESET)
            send_email(user+"@furgason.com",msg)
            return render_template('confirmation.html', resetPasswd=True, token_id=token_id)

    if request.method == 'POST' and form.validate():
        password = form.passwd.data
        print(f"Token_id from confirmation: {token_id}")

        ms = imaplib.IMAP4_SSL(MAIL_VALIDATION_ADDR)
        email_account = username.lower() + EMAIL_DOMAIN

        print(email_account)

        try:
            print(ms.login(email_account,password))
            login_success = True
        except ms.error as e:
            if 'authentication failed' in str(e):
                # print(f"Auth failed with error: {e}")
                flash('Authentication validation failed!  Please check your password and resubmit it for validation.')
            login_success = False

        if login_success:
            store_password(token_id,encrypt_string(password))
            msg = SET_EMAIL_PASSWORD_MSG.replace("[[recipient name]]",user)
            msg = msg.replace("[[recipient preferences]]",PREF_STORE)
            send_email(user+EMAIL_DOMAIN,msg)
            return render_template('confirmation.html', password=password, token_id=token_id)
    return render_template('passwd.html', form=form, user=user)
