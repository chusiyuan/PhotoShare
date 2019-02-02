from PhotoShare import app, db
from flask import render_template, redirect, request, flash, get_flashed_messages
from PhotoShare.models import User, Image, Comment
import random
import hashlib
from flask_login import login_user, logout_user, login_required, current_user
import json


@app.route('/')
def index():
    # images = Image.query.order_by(Image.id.desc()).limit(10).all()
    paginate = Image.query.order_by(Image.id.desc()).paginate(page=1, per_page=10, error_out=False)
    return render_template('index.html', images=paginate.items, has_next=paginate.has_next)


@app.route('/home/<int:page>/<int:per_page>/')
def home_images(page, per_page):
    paginate = Image.query.order_by(Image.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    data = {'has_next': paginate.has_next}
    images = []
    for image in paginate.items:
        user = User.query.get(image.user_id)
        comments = []
        for comment in image.comments:
            m = {'user_id': comment.user.id, 'username': comment.user.username, 'content': comment.content }
            comments.append(m)
        img = {'id': image.id, 'url': image.url, 'created_date': image.created_date.strftime('%Y-%m-%d %H:%M:%S'),
               'user_id': image.user_id, 'username': user.username, 'head_url': user.head_url, 'comments': comments}
        images.append(img)
    data['images'] = images
    return json.dumps(data)


@app.route('/image/<int:image_id>/')
def image(image_id):
    image = Image.query.get(image_id)
    if image == None:
        return redirect('/')
    return render_template('pageDetail.html', image=image)


@app.route('/profile/<int:user_id>/')
@login_required
def profile(user_id):
    user = User.query.get(user_id)
    if user == None:
        return redirect('/')

    paginate = Image.query.filter_by(user_id=user_id).paginate(page=1, per_page=3, error_out=False)
    return render_template('profile.html', user=user, has_next=paginate.has_next, images=paginate.items)


@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_images(user_id, page, per_page):
    paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page)
    images = []
    data = {'has_next': paginate.has_next}
    for image in paginate.items:
        img = {'id': image.id, 'url': image.url, 'comments_count': len(image.comments)}
        images.append(img)
    data['images'] = images
    return json.dumps(data)


@app.route('/reglogin/', methods=['get', 'post'])
def reglogin(msg=''):
    logout_user()
    for m in get_flashed_messages(category_filter=['reglogin']):
        msg += m
    return render_template('login.html', msg=msg)


@app.route('/reg/', methods=['get', 'post'])
def reg():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    if username == '' or password == '':
        flash('用户名或密码不能为空', category='reglogin')
        return redirect('/reglogin/')
    user = User.query.filter_by(username=username).first()
    if user != None:
        flash('用户名已被注册', category='reglogin')
        return redirect('/reglogin/')
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    salt = ''
    for i in range(10):
        salt += chars[random.randint(0, len(chars)-1)]
    m = hashlib.md5()
    m.update((password + salt).encode('utf8'))
    password = m.hexdigest()
    user = User(username, password, salt)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    next = request.values.get('next')
    if next != None and next.startswith('/') > 0:
        return redirect(next)
    return redirect('/')


@app.route('/login/', methods=['get', 'post'])
def login():
    username = request.values.get('username').strip()
    password = request.values.get('password').strip()
    if username == '' or password == '':
        flash('用户名或密码不能为空', category='reglogin')
        return redirect('/reglogin/')
    user = User.query.filter_by(username=username).first()
    if user == None:
        flash('用户名不存在', category='reglogin')
        return redirect('/reglogin/')
    m = hashlib.md5()
    m.update((password + user.salt).encode('utf8'))
    if user.password != m.hexdigest():
        flash('密码错误', category='reglogin')
        return redirect('/reglogin/')

    login_user(user)
    next = request.values.get('next')
    if next != None and next.startswith('/') > 0:
        return redirect(next)
    return redirect('/')


@app.route('/upload/', method=['post'])
def upload():

