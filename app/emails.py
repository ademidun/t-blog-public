from flask.ext.mail import Message, smtplib
from app import app, mail
from threading import Thread
from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except (socket.error,socket.timeout,smtplib.SMTPException,smtplib.SMTPConnectError):
            #if e.errno == errno.ECONNREFUSED:
            flash('The email notification did not send.', 'error')
        

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)
    
    
from flask import render_template
from config import ADMINS

def follower_notification(followed, follower):
    send_email("[microblog] %s is now following you!" % follower.nickname,
               ADMINS[0],
               [followed.email],
               render_template("follower_email.txt", 
                               user=followed, follower=follower),
               render_template("follower_email.html", 
                               user=followed, follower=follower))