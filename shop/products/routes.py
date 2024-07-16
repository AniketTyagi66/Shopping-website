from flask import redirect, render_template, url_for, request, flash, session, current_app
from shop import db, app, photos, search
from .models import Brand, Category, Addproduct
from .forms import Addproducts,CSRFForm
import secrets, os


def brands():
    brands = Brand.query.join(Addproduct, (Brand.id==Addproduct.brand_id)).all()
    return brands


def categories():
    categories = Category.query.join(Addproduct, (Category.id==Addproduct.category_id)).all()
    return categories



@app.route('/')
def home():
    if 'email' not in session:
        return redirect(url_for('login'))
    form = CSRFForm()
    page = request.args.get('page', 1, type=int)
    products=Addproduct.query.filter(Addproduct.stock > 0).order_by(Addproduct.id.desc()).paginate(page=page, per_page=4)
    return render_template("products/index.html", products=products,brands=brands(),categories=categories(),form=form)

@app.route('/result')
def result():
    form = CSRFForm()
    searchword = request.args.get('q')
    products=Addproduct.query.msearch(searchword, fields=['name','desc'], limit=6)
    return render_template("products/result.html", products=products, brands=brands(),categories=categories(),form=form)


@app.route('/product/<int:id>')
def single_page(id):
    form = CSRFForm()
    product=Addproduct.query.get_or_404(id)
    return render_template("products/single_page.html",product=product,brands=brands(),categories=categories(),form=form)


@app.route('/brand/<int:id>')
def get_brand(id):
    form = CSRFForm()
    get_b=Brand.query.filter_by(id=id).first_or_404()
    page = request.args.get('page', 1, type=int)
    brand = Addproduct.query.filter_by(brand=get_b).paginate(page=page, per_page=4)
    return render_template("products/index.html", brand=brand, brands=brands(), categories=categories(),get_b=get_b,form=form)

@app.route('/categories/<int:id>')
def get_category(id):
    form = CSRFForm()
    page = request.args.get('page', 1, type=int)
    get_cat= Category.query.filter_by(id=id).first_or_404()
    get_cat_prod = Addproduct.query.filter_by(category=get_cat).paginate(page=page, per_page=4)
    return render_template("products/index.html", get_cat_prod=get_cat_prod, categories=categories(),brands=brands(), get_cat=get_cat,form=form)

    
@app.route('/addbrand', methods=['GET','POST'])
def addbrand():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    
    form = CSRFForm()
    if request.method=="POST" and form.validate_on_submit():
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addbrand'))
    return render_template('products/addbrand.html', brands='brand',form=form)

@app.route('/updatebrand/<int:id>', methods=['GET','POST'])
def updatebrand(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        # return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    form = CSRFForm()
    if request.method=="POST":
        updatebrand.name = brand
        # db.session.add(brand)
        flash(f'Your Brand has been updated', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html', title='update brand page', updatebrand=updatebrand,form=form)


@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
   brand = Brand.query.get_or_404(id)
   if request.method=="POST":
       db.session.delete(brand)
       db.session.commit()
       flash(f'The brand {brand.name} deleted from your database','success')
       return redirect(url_for('admin'))
   flash(f'The brand {brand.name} cant from be deleted','warning')
   return redirect(url_for('admin'))
    
    

@app.route('/addcat', methods=['GET','POST'])
def addcat():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    
    form = CSRFForm()
    if request.method=="POST":
        getcategory = request.form.get('category')
        cat = Category(name=getcategory)
        db.session.add(cat)
        flash(f'The Category {getcategory} added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addcat'))
    return render_template('products/addbrand.html',form=form)


@app.route('/updatecat/<int:id>', methods=['GET','POST'])
def updatecat(id):
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        # return redirect(url_for('login'))
    updatecat = Category.query.get_or_404(id)
    category = request.form.get('category')
    form = CSRFForm()
    if request.method=="POST":
        updatecat.name = category
        # db.session.add(brand)
        flash(f'Your Category has been updated', 'success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/updatebrand.html', title='update category page', updatecat=updatecat,form=form)


@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
   category = Category.query.get_or_404(id)
   if request.method=="POST":
       db.session.delete(category)
       db.session.commit()
       flash(f'The category {category.name} deleted from your database','success')
       return redirect(url_for('admin'))
   flash(f'The category {category.name} cant from be deleted','warning')
   return redirect(url_for('admin'))
    


@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    if 'email' not in session:
        flash(f'Please login first', 'danger')
        return redirect(url_for('login'))
    
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts()

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        discount = float(form.discount.data)
        stock = form.stock.data
        colors = form.colors.data
        desc = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')

        try:
            image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        except Exception as e:
            flash(f'An error occurred while uploading the images: {e}', 'danger')
            return render_template('products/addproduct.html', title="Add Product", form=form, brands=brands, categories=categories)

        addpro = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors, desc=desc,
                            brand_id=brand, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3)

        try:
            db.session.add(addpro)
            db.session.commit()
            flash(f'The product {name} has been added to your database', 'success')
            return redirect(url_for('admin'))
        except Exception as e:
            # db.session.rollback()
            flash(f'An error occurred while adding the product: {e}', 'danger')

    return render_template('products/addproduct.html', title="Add Product", form=form, brands=brands, categories=categories)



@app.route('/updateproduct/<int:id>', methods=['GET','POST'])
def updateproduct(id):
    brands= Brand.query.all()
    categories= Category.query.all()
    product = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = Addproducts(request.form)
    if request.method == "POST":
        product.name=form.name.data
        product.price=form.price.data
        product.discount=form.discount.data
        product.brand_id=brand
        product.category_id=category
        product.stock=form.stock.data
        product.colors=form.colors.data
        product.desc=form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1=photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1=photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_1=photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1=photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_1=photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                product.image_1=photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")


        db.session.commit()
        flash(f'your product has been updated','success')
        return redirect(url_for('admin'))

    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.desc

    return render_template('products/updateproduct.html', form=form, brands=brands,categories=categories, product=product)


@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
   product = Addproduct.query.get_or_404(id)
   if request.method=="POST":
       try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
       except Exception as e:
            print(e) 
          
       db.session.delete(product)
       db.session.commit()
       flash(f'The product {product.name} deleted from your database','success')
       return redirect(url_for('admin'))
   flash(f'The product {product.name} cant from be deleted','warning')
   return redirect(url_for('admin'))