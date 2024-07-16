from flask import render_template,session,request,redirect,url_for,flash,jsonify

from shop import app,db, bcrypt
from .forms import RegistrationForm, LoginForm
from shop.products.models import Addproduct, Brand, Category
from .models import User
import uuid
from sqlalchemy.exc import IntegrityError
from shop.products.forms import CSRFForm

from flask_login import login_user, logout_user, current_user, login_required
# import jwt
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_jwt_extended import decode_token


app.config['SECRET_KEY'] = 'hvashxassxj14266'
# app.config['JWT_SECRET_KEY'] = 'jhichsbscsjscschussufdsjsdhudsx'  # Change this to a strong secret key

jwt = JWTManager(app)

@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    form = CSRFForm()
    products =  Addproduct.query.all()
    return render_template('admin/index.html', title='Admin Page', products=products,form=form)


@app.route('/brands')
def brands():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    form = CSRFForm()
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', title="Brand page", brands=brands,form=form)

@app.route('/category')
def category():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    form = CSRFForm()
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html', title="Brand page", categories=categories,form=form)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate_on_submit():
        existing_user_username = User.query.filter_by(username=form.username.data).first()
        existing_user_email = User.query.filter_by(email=form.email.data).first()
        if existing_user_username:
            flash('Username already exists. Please choose a different one.', 'danger')
        elif existing_user_email:
            flash('Email already registered. Please use a different email or log in.', 'danger')
        else:
            try:
                hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                unique_profile_filename = f"profile_{uuid.uuid4().hex}.jpg"
                user = User(name=form.name.data, username=form.username.data, email=form.email.data,
                            password=hash_password, profile=unique_profile_filename)
                db.session.add(user)
                db.session.commit()
                flash(f'Welcome {form.name.data}! Thank you for registering.', 'success')

                access_token = create_access_token(identity={'email': form.email.data})
                return redirect(url_for('protected', token=access_token))
            except IntegrityError as e:
                db.session.rollback()
                flash(f'Database error: {str(e.orig)}', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Unexpected error: {str(e)}', 'danger')
    return render_template('admin/register.html', form=form, title="Registration Page")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == "POST" and form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            access_token = create_access_token(identity={'email': form.email.data})
            session['email'] = form.email.data  # Set the email in session
            return redirect(url_for('protected', token=access_token))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('admin/login.html', form=form, title="Login Page")


@app.route('/protected', methods=['GET'])
@jwt_required(optional=True)
def protected():
    current_user = get_jwt_identity()
    if request.headers.get('Authorization'):
        if current_user:
            return jsonify(logged_in_as=current_user), 200
        else:
            return jsonify({"msg": "You are not logged in!"}), 401
    else:
        token = request.args.get('token')
        if token:
            try:
                decoded_token = decode_token(token)
                email = decoded_token['sub']['email']
                return redirect(url_for('home'))  # Redirect to home if token is valid
            except Exception as e:
                return jsonify({"msg": str(e)}), 401
        return redirect(url_for('login'))




@app.route('/logout')
def logout():
    session.pop('email', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
