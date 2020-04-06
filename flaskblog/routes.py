import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Community, Page, Entry, Goal
from flask_login import login_user, current_user, logout_user, login_required
from collections import defaultdict
import json

@app.route("/home", methods=['GET', 'POST'])
@login_required
def home():
    # get users for potentential new firnds
    users = User.query.all()
    # remove current user
    users = [user for user in users if user.id != current_user.id and user not in current_user.friends]

    entries = defaultdict(list)
    goals = defaultdict(list)
    for friend in current_user.friends:
        for page in friend.pages:
            entries[friend].extend(Entry.query.filter_by(page_id=page.id).all())
            goals[friend].extend(Goal.query.filter_by(page_id=page.id).all())
    return render_template('home.html', entries=entries, goals=goals, users=users)


@app.route("/journal")
@login_required
def journal():
    pages = Page.query.filter_by(user_id=current_user.id).all()
    # get users for potentential new firnds
    users = User.query.all()
    # remove current user
    users = [user for user in users if user.id != current_user.id and user not in current_user.friends]

    entries = {}
    goals = {}
    for page in pages:
        entries[page.id] = Entry.query.filter_by(page_id=page.id).all()
        goals[page.id] = Goal.query.filter_by(page_id=page.id).all()

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    return render_template('profile.html', pages=pages, entries=entries, goals=goals, 
                        image_file=image_file, users=users)


@app.route("/journal/<int:user_id>")
@login_required
def spectate(user_id):
    # get users for potentential new firnds
    users = User.query.all()
    # remove current user
    users = [user for user in users if user.id != current_user.id and user not in current_user.friends]

    if user_id == current_user.id:
        return redirect(url_for('home'))
    other_user = User.query.filter_by(id=user_id).first()
    pages = Page.query.filter_by(user_id=user_id).all()
    entries = {}
    goals = {}
    for page in pages:
        entries[page.id] = Entry.query.filter_by(page_id=page.id).all()
        goals[page.id] = Goal.query.filter_by(page_id=page.id).all()
    image_file = url_for('static', filename='profile_pics/' + other_user.image_file)
    return render_template('other_profile.html', pages=pages, entries=entries, goals=goals, 
                    image_file=image_file, other_user=other_user, users=users)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print(form.remember.data)
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/page", methods=['POST', 'PUT'])
# @login_required
def new_page():
    if request.method == 'POST':
        args = request.form
        if not args:
            abort(400)
        if not current_user.is_authenticated:
            abort(403)

        title = args['title']
        page = Page(user_id=current_user.id, title=title)
        db.session.add(page)
        db.session.commit()

        return json.dumps({'success':True,  'page_id': page.id}), 200, {'ContentType':'application/json'}

    elif request.method == 'PUT':
        args = request.form
        if not args:
            abort(400)
        if not current_user.is_authenticated:
            abort(403)

        page_id = args['page_id']
        new_title = args['title']
        page = Page.query.filter_by(id=page_id).first()
        page.title = new_title
        db.session.commit()

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route("/entry", methods=['POST', 'PUT'])
@login_required
def new_entry():
    if request.method == 'POST':
        args = request.form
        if not args:
            abort(400)
        if not current_user.is_authenticated:
            abort(403)

        page_id = args['page_id']
        text = args['text']

        entry = Entry(page_id=page_id, text=text)
        db.session.add(entry)
        db.session.commit()

        return json.dumps({'success':True, 'entry_id': entry.id}), 200, {'ContentType':'application/json'}

    elif request.method == 'PUT':
        args = request.form
        if not args:
            abort(400)
        if not current_user.is_authenticated:
            abort(403)

        entry_id = args['entry_id']
        new_text = args['text']

        entry = Entry.query.filter_by(id=entry_id).first()
        entry.text = new_text
        db.session.commit()

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route("/goal", methods=['POST', 'PUT'])
@login_required
def new_goal():
    if request.method == 'POST':
        args = request.form
        if not args:
            abort(400)
        if not current_user.is_authenticated:
            abort(403)

        page_id = args['page_id']
        text = args['text']
        goal = Goal(page_id=page_id, text=text)
        db.session.add(goal)
        db.session.commit()

        return json.dumps({'success':True, 'goal_id': goal.id}), 200, {'ContentType':'application/json'}
    
    elif request.method == 'PUT':
        args = request.form
        if not args:
            abort(400)
        if not current_user.is_authenticated:
            abort(403)

        goal_id = args['goal_id']
        new_goals = args['goals']

        goal = Goal.query.filter_by(id=goal_id).first()
        goal.goals = new_goals
        db.session.commit()

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route("/comment", methods=['POST', 'PUT'])
@login_required
def new_comment():
    if request.method == 'POST':
        args = request.form
        if not args:
            abort(400)
        if not current_user.is_authenticated:
            abort(403)

        entry_id = args.get('entry_id')
        goal_id = args.get('goal_id')
        text = args.get('text')
        user_id = args.get('user_id')

        if entry_id:
            comment = Comment(text=text, user_id=user_id, username = current_user.username,
                                    entry_id=entry_id)
        elif goal_id:
            comment = Comment(text=text, user_id=user_id, username = current_user.username,
                                    goal_id=goal_id)
            
        db.session.add(comment)
        db.session.commit()

        return json.dumps({'success':True, 'comment_id': comment.id}), 200, {'ContentType':'application/json'}
    
    elif request.method == 'PUT':
        args = request.form
        if not args:
            abort(400)
        if not current_user.is_authenticated:
            abort(403)
        
        # if the current user is that the original poster
        user_id = args['user_id']
        if user_id != current_user.id:
            abort(403)
        comment_id = args['comment_id']
        new_text = args['text']
        
        comment = Comment.query.filter_by(id=comment_id).first()
        comment.text = new_text
        db.session.commit()

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route("/friend", methods=['POST'])
@login_required
def new_friend():
    args = request.form
    if not args:
        abort(400)
    if not current_user.is_authenticated:
        abort(403)

    user_id = args['user_id']
    new_friend = User.query.filter_by(id=user_id).first()
    current_user.friends.append(new_friend)
    new_friend.friends.append(current_user)

    db.session.commit()

    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}  

# @app.route("/post/new", methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = PostForm()
#     if form.validate_on_submit():
#         post = Post(title=form.title.data, content=form.content.data, author=current_user)
#         db.session.add(post)
#         db.session.commit()
#         flash('Your post has been created!', 'success')
#         return redirect(url_for('home'))
#     return render_template('create_post.html', title='New Post',
#                            form=form, legend='New Post')


# @app.route("/post/<int:post_id>")
# def post(post_id):
#     post = Post.query.get_or_404(post_id)
#     return render_template('post.html', title=post.title, post=post)


# @app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
# @login_required
# def update_post(post_id):
#     post = Post.query.get_or_404(post_id)
#     if post.author != current_user:
#         abort(403)
#     form = PostForm()
#     if form.validate_on_submit():
#         post.title = form.title.data
#         post.content = form.content.data
#         db.session.commit()
#         flash('Your post has been updated!', 'success')
#         return redirect(url_for('post', post_id=post.id))
#     elif request.method == 'GET':
#         form.title.data = post.title
#         form.content.data = post.content
#     return render_template('create_post.html', title='Update Post',
#                            form=form, legend='Update Post')


# @app.route("/post/<int:post_id>/delete", methods=['POST'])
# @login_required
# def delete_post(post_id):
#     post = Post.query.get_or_404(post_id)
#     if post.author != current_user:
#         abort(403)
#     db.session.delete(post)
#     db.session.commit()
#     flash('Your post has been deleted!', 'success')
#     return redirect(url_for('home'))

# @app.route("/user/<string:username>")
# def user_posts(username):
#     page = request.args.get('page', 1, type=int)
#     user = User.query.filter_by(username=username).first_or_404()
#     posts = Post.query.filter_by(author=user)\
#         .order_by(Post.date_posted.desc())\
#         .paginate(page=page, per_page=5)
#     return render_template('user_posts.html', posts=posts, user=user)
