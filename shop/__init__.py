from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads, patch_request_class
from flask_msearch import Search
from flask_wtf.csrf import CSRFProtect
import os
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_url_path='/static')


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:A2306niket#@localhost/ecommerse"
app.config['SECRET_KEY'] = 'hvashxassxj14266'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')
images_path = os.path.join(basedir, 'static/images')
if not os.path.exists(images_path):
    os.makedirs(images_path)
app.config['UPLOADED_PHOTOS_DEST'] = images_path
app.config['JWT_SECRET_KEY'] = 'jhichsbscsjscschussufdsjsdhudsx'  # Change this to a strong secret key

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app, 16 * 1024 * 1024)  # Set max upload size to 16 MB

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
jwt = JWTManager(app)  # Initialize JWT manager



# Initialize flask_msearch
search = Search(db=db)
search.init_app(app)

migrate=Migrate(app,db)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='customerLogin'
login_manager.needs_refresh_message_category='danger'
login_manager.login_message = u"Please login first"


# Import models and routes within application context
with app.app_context():
    try:
        # Import models after initializing db to avoid circular imports
        from shop.products.models import Addproduct
        print("Addproduct model imported")

        # Import routes after initializing extensions
        from shop.admin import routes
        from shop.products import routes
        from shop.carts import carts
        from shop.customers import routes
        print("Routes imported")

        # Ensure all tables are created
        db.create_all()
        print("Database tables created")
    except Exception as e:
        print(f"Error during app context setup: {e}")
