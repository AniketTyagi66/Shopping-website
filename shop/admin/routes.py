from flask import render_template,session,request,redirect,url_for,flash

from shop import app,db, bcrypt
from .forms import RegistrationForm, LoginForm
from shop.products.models import Addproduct, Brand, Category
from .models import User
import uuid
from sqlalchemy.exc import IntegrityError


@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    products =  Addproduct.query.all()
    return render_template('admin/index.html', title='Admin Page', products=products)


@app.route('/brands')
def brands():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', title="Brand page", brands=brands)

@app.route('/category')
def category():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html', title="Brand page", categories=categories)



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        existing_user_username = User.query.filter_by(username=form.username.data).first()
        existing_user_email = User.query.filter_by(email=form.email.data).first()
        if existing_user_username:
            flash('Username already exists. Please choose a different one.', 'danger')
        elif existing_user_email:
            flash('Email already registered. Please use a different email or log in.', 'danger')
        else:
            try:
                hash_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                # Generate a unique profile picture filename
                unique_profile_filename = f"profile_{uuid.uuid4().hex}.jpg"
                user = User(name=form.name.data, username=form.username.data, email=form.email.data,
                            password=hash_password, profile=unique_profile_filename)
                db.session.add(user)
                db.session.commit()
                flash(f'Welcome {form.name.data}! Thank you for registering.', 'success')
                return redirect(url_for('home'))
            except IntegrityError as e:
                db.session.rollback()
                flash(f'Database error: {str(e.orig)}', 'danger')
            except Exception as e:
                db.session.rollback()
                flash(f'Unexpected error: {str(e)}', 'danger')
    return render_template('admin/register.html', form=form, title="Registration Page")


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm(request.form)
#     if request.method == 'POST' and form.validate():
#         hash_password = bcrypt.generate_password_hash(form.password.data)
#         user = User(name = form.name.data, username = form.username.data, email = form.email.data,
#                     password = hash_password)
#         db.session.add(user)
#         db.session.commit()
#         flash(f'Welcome {form.name.data} Thanks You for registering','success')
#         return redirect(url_for('home'))
#     return render_template('admin/register.html', form=form, title="Registeration page")

@app.route('/login', methods=['GET','POST'])
def login():
    form=LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email= form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            flash(f'Welcome {form.email.data} you are logedin now', 'success')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Wrong Password please try again', "danger")
    return render_template('admin/login.html', form = form, title= "Login Page")