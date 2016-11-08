from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
#./run.py
import os
from flask.ext.login import LoginManager
from flask.ext.openid import OpenID
from config import basedir
from flask.ext.mail import Mail
#for translation stuff
from flask.ext.babel import Babel

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
mail = Mail(app)
babel = Babel(app)    

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'
oid = OpenID(app, os.path.join(basedir, 'tmp'))


from app import views, models

from config import basedir, ADMINS , Config
#MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
MAIL_SERVER =Config.MAIL_SERVER
MAIL_PASSWORD =Config.MAIL_PASSWORD
MAIL_PORT =Config.MAIL_PORT
MAIL_USERNAME =Config.MAIL_USERNAME

#for sending debugging logs to emails
if not app.debug:
    import logging
    from logging.handlers import SMTPHandler
    credentials = None
    if MAIL_USERNAME or MAIL_PASSWORD:
        credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    mail_handler = SMTPHandler((MAIL_SERVER, MAIL_PORT), 'no-reply@' + MAIL_SERVER, ADMINS, 'microblog failure', credentials)
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

#for writing debugging logs to files   
if not app.debug and os.environ.get('HEROKU') is None:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/microblog.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('microblog startup')

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('microblog startup')
        
#for timezone stuff
from .momentjs import momentjs
app.jinja_env.globals['momentjs'] = momentjs

#incase you need to re-disable Google's 'less secure apps' feature
# visit https://www.google.com/settings/security/lesssecureapps
    









