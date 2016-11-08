from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required, LoginManager
from app import app, db, lm, oid, babel
from .forms import LoginForm, EditForm, PostForm, ProfilePicForm
from .models import User, Post
from datetime import datetime
from config import POSTS_PER_PAGE
from config import LANGUAGES
from guess_language import guessLanguage
import string

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = PostForm()
    if form.validate_on_submit():
    	language = guessLanguage(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, timestamp=datetime.utcnow(), author=g.user,language=language)
        db.session.add(post)
        db.session.commit()
        flash(gettext('Your post is now live!'))
        return redirect(url_for('index'))
    posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    return render_template('index.html',
                           title='Home',
                           form=form,
                           posts=posts)
                           
@app.route('/logout')
def logout():
    logout = 'true'
    logout_user()
    return redirect(url_for('index'))
                         
@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html', 
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])
   


                
@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())

from flask.ext.babel import gettext
@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash(gettext('Invalid login. Please try again.'))
        return redirect(url_for('logout'))
    user = User.query.filter_by(email=resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_valid_nickname(nickname)
        nickname = User.make_unique_nickname(nickname)
        nickname = nickname.lower()
        user = User(nickname=nickname, email=resp.email)
        db.session.add(user)
        db.session.commit()
        # make the user follow him/herself
        db.session.add(user.follow(user))
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('index'))

from forms import SearchForm
import os

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        g.search_form = SearchForm()
        db.session.add(g.user)
        db.session.commit()

@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
#@login_required
def user(nickname, page=1):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if g.user.get_id() is not None:
        posts = g.user.followed_posts().paginate(page, POSTS_PER_PAGE, False)
    else:
        posts=Post.query.filter_by(user_id=user.id).paginate(page, POSTS_PER_PAGE, False)
    if not user.is_following(user):
        user.followed.append(user)
    profpic = 'img/profpic/%s.jpg' % user.nickname
    return render_template('user.html',
                           user=user,
                           posts=posts, profpic=profpic)
from werkzeug.utils import secure_filename

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    #largest file size is 4mb
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
    form = EditForm(g.user.nickname)
    pic_form = ProfilePicForm()
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        app.config.from_object('config')
        if pic_form.validate_on_submit():
            profpic= pic_form.profile_pic.data
            print (profpic)
            profpicpath= url_for('static', filename='img/profpic/%s.jpg' % g.user.nickname)
            profpicpath=profpicpath.replace("/","",1)
            print ('Profpicpath: %s ' % profpicpath)
            #with open(profpicpath, "w+") as fo:
            #    foo_bar='dummy variable, creating directory to save image'
            #os.path.join(app.config['UPLOAD_PATH'], '%s.jpg' % g.user.nickname)
            #profpic.save(profpicpath)
            APP_ROOT = os.path.dirname(os.path.abspath(__file__))
            UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/img/profpic')
            app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
            profpic.save(os.path.join(app.config['UPLOAD_FOLDER'], '%s.jpg' % g.user.nickname))
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html', form=form,pic_form=pic_form)
    
from .emails import follower_notification
import socket, errno, smtplib
@app.route('/follow/<nickname>')
@login_required
def follow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.follow(user)
    if u is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You are now following ' + nickname + '!')
    try:
        follower_notification(user, g.user)
    except (socket.error,socket.timeout,smtplib.SMTPException,smtplib.SMTPConnectError):
        #if e.errno == errno.ECONNREFUSED:
        flash('The email notification did not send.', 'error')
    return redirect(url_for('user', nickname=nickname))
    
    
    
    #else:
        #raise
    # try:
#       
#     except socket.error, v:
#       errorcode=v[0]
#       if errorcode==errno.ECONNREFUSED:
#           
    



@app.route('/unfollow/<nickname>')
@login_required
def unfollow(nickname):
    user = User.query.filter_by(nickname=nickname).first()
    if user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname=nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname=nickname))
    db.session.add(u)
    db.session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname=nickname))

# we do not load the search results directly because
#if the user refreshes the browser, instead of the form
#being resubmitted, the results page will be reloaded
@app.route('/search', methods = ['POST'])
@login_required
def search():
    if not g.search_form.validate_on_submit():
        return redirect(url_for('index'))
    return redirect(url_for('search-results', query=g.search_form.search.data))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    if post is None:
        flash('Post not found.')
        return redirect(url_for('index'))
    if post.author.id != g.user.id:
        flash('You cannot delete this post.')
        return redirect(url_for('index'))
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted.')
    return redirect(url_for('index'))
        
from config import MAX_SEARCH_RESULTS

@app.route('/search-results')
@app.route('/search-results/<query>')
@login_required
def search_results(query):
    results=Post.query.whoosh_search(query, MAX_SEARCH_RESULTS).all()
    return render_template('search-results.html',
                           query=query,
                           results=results)
                           
from flask.ext.sqlalchemy import get_debug_queries
from config import DATABASE_QUERY_TIMEOUT

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement, query.parameters, query.duration, query.context))
    return response
    
@app.route('/about')
def about():
    nicknames = {'galbraith': 'galbraith', 'keynes': 'keynes', 'dup': 'dup'}
    return render_template('about.html',title='About')

    
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
