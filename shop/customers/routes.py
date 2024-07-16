from flask import redirect, render_template, url_for, request, flash, session, current_app, json, make_response
from flask_login import login_required,current_user,logout_user,login_user
from shop import db, app, photos, search, bcrypt
from .forms import CustomerRegisterForm, CustomerLoginForm
from .model import Register, CustomerOrder
import secrets, os
import pdfkit
import stripe
from shop.products.routes import brands,categories
from shop.products.forms import CSRFForm

# Path to wkhtmltopdf executable
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Update this path if needed
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

publishable_key = "pk_test_51PXmIdJQmatrvl4bs1la24nBUbgMVHWNB0VETkgJLw9mOXT7SuZ0T4Nha4XV0FZP2zyWt0UytjDqMNwb4iLywg8q00psdRYIkY"

stripe.api_key = "sk_test_51PXmIdJQmatrvl4bNvlUxYTXipaIBQsO1uT18199fPonmmkYQHTYDqo74rhpwPpdZ75kwtCdQwgMCmESvv8yUBud00sDnRAKSI"


@app.route('/payment', methods=["POST"])
@login_required
def payment():
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        description='Myshop',
        amount=amount,
        currency='usd',
    )
    orders = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).first()
    orders.status='Paid'
    db.session.commit()
    return redirect(url_for('thanks'))

@app.route('/thanks')
def thanks():
    return render_template('customer/thank.html')


#create
@app.route('/customer/register', methods=['GET','POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password=bcrypt.generate_password_hash(form.password.data)
        register=Register(name=form.name.data, username=form.username.data, email=form.email.data,contact=form.contact.data, password=hash_password, 
                          country=form.country.data, city=form.city.data, address=form.address.data,
                          zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data} thankyou for registering','success')
        db.session.commit()
        return redirect(url_for('login'))
    else:
        print(form.errors)
    return render_template('customer/register.html',form=form)

#read
@app.route('/customer/login', methods=['GET','POST'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('you are login now!','success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email and password','danger')
        return redirect(url_for('customerLogin'))

    return render_template('customer/login.html',form=form)



@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('home'))


#remove unwanted details from shoping cart
def upadteshoppingcart():
    for _key, product in session['Shoppingcart'].items():
        session.modified=True
        del product['image']
        del product['colors']
    return upadteshoppingcart


@app.route('/getorder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id=current_user.id
        invoice=secrets.token_hex(5)
        upadteshoppingcart()
        print(invoice)
        try:
            shopping_cart_json = json.dumps(session['Shoppingcart'])
            order=CustomerOrder(invoice=invoice,customer_id=customer_id,orders=shopping_cart_json)
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully','success')
            return redirect(url_for('orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash('Some thing went wrong while order','danger')
            return redirect(url_for('getCart'))
        


@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        customer_id = current_user.id
        customer = Register.query.get(customer_id)
        orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).first()

        if orders:
            orders_data = json.loads(orders.orders)  # Deserialize JSON string
            subTotal = 0.0
            grandTotal = 0.0

            form = CSRFForm()
            for _key, product in orders_data.items():
                discount = (product.get('discount', 0) / 100) * float(product.get('price', 0))
                subTotal += (float(product.get('price', 0)) - discount) * int(product.get('quantity', 0))

            tax = subTotal * 0.06
            # grandTotal = subTotal * 1.06
            grandTotal = ("%.2f" % (1.06 * float(subTotal)))

            return render_template('customer/order.html', invoice=invoice, tax=tax, subTotal=subTotal, grandTotal=grandTotal, customer=customer, orders_data=orders_data,orders=orders,
                                   brands=brands(),categories=categories(),form=form)
        else:
            flash("Order not found", "error")
            return redirect(url_for('customerLogin'))
    else:
        return redirect(url_for('customerLogin'))
    


@app.route('/get_pdf/<invoice>', methods=["POST"])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandTotal=0
        subTotal =0
        tax=0
        customer_id=current_user.id
        if request.method == "POST":
            form = CSRFForm()
            customer = Register.query.filter_by(id=customer_id).first()
            orders = CustomerOrder.query.filter_by(customer_id=customer_id, invoice=invoice).first()
            orders_data = json.loads(orders.orders)
            for _key, product in orders_data.items():
                discount = (product.get('discount', 0) / 100) * float(product.get('price', 0))
                subTotal += (float(product.get('price', 0)) - discount) * int(product.get('quantity', 0))

            tax = subTotal * 0.06
            grandTotal = subTotal * 1.06

            rendered = render_template('customer/pdf.html',invoice=invoice, tax=tax, grandTotal=grandTotal,
                                customer=customer,orders_data=orders_data,orders=orders,form=form)
            pdf = pdfkit.from_string(rendered, False,configuration=config)
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'atteched; filename='+invoice+'.pdf'
            return response
    return redirect(url_for('orders'))


    