# -*- coding: utf-8 -*-
#because Espanol has a foreign letter 'n'
#we must tell the Python interpreter that we are using the UTF-8 encoding and not ASCII

# ...
import os
from os.path import join, dirname, realpath
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_PATH = join(dirname(realpath(__file__)), 'static/img/profpic')

CSRF_ENABLED = True
#SECRET_KEY = 'you-will-never-guess'
SECRET_KEY = 'secret-key-goes-here'
os.environ['SECRET_KEY']='another-secret-key-goes-here'


OPENID_PROVIDERS = [
    {'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id'},
    {'name': 'Yahoo', 'url': 'https://me.yahoo.com'},
    {'name': 'AOL', 'url': 'http://openid.aol.com/<username>'},
    {'name': 'Flickr', 'url': 'http://www.flickr.com/<username>'},
    {'name': 'MyOpenID', 'url': 'https://www.myopenid.com'}]
    

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5


# administrator list
ADMINS = ['admin@mail.ca']


# pagination
POSTS_PER_PAGE = 3

#Whoosh-SqlAlchemy integration
WHOOSH_BASE = os.path.join(basedir, 'search.db')

MAX_SEARCH_RESULTS = 50

MAX_CONTENT_LENGTH = 4 * 1024 * 1024

class Config:
    SECRET_KEY =              os.environ.get('SECRET_KEY',        'SECRET_KEY')
    SSL_DISABLE = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLCLCHEMY_RECORD_QUERIES = True
    CSRF_ENABLED = True
    MAIL_SERVER =               os.environ.get('MAIL_SERVER',          'smtp.gmail.com')
    MAIL_USERNAME =         os.environ.get('MAIL_USERNAME',     '')
    MAIL_PASSWORD =         os.environ.get('MAIL_PASSWORD',     '')
    MAIL_SENDER =              os.environ.get('MAIL_SENDER', 'Project Admin<>')
    PROJECT_ADMIN =         os.environ.get('PROJECT_ADMIN',     'PROJECT_ADMIN')
    MAIL_PORT =              int(os.environ.get('MAIL_PORT',         '465'))
    MAIL_USE_TLS =        int(os.environ.get('MAIL_USE_TLS',  True))
    MAIL_USE_SSL =        int(os.environ.get('MAIL_USE_SSL',  False))
    MAIL_SUBJECT_PREFIX = '[PROJECT]'
    

# available languages
LANGUAGES = {
    'en': 'English',
    'es': 'Español'
}