from flask import Flask, flash, render_template, request, url_for, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from telemetry_setup import instrument_app
from structured_logging import configure_logging
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

app = Flask(__name__)

@app.route("/test-500")
def test_500():
    raise RuntimeError("STARCOURT_TEST_500")

instrument_app(app)
logger = configure_logging()

#FOR FLASH CNXN
app.secret_key = "starcourt-dev-secret-key"


#DB CONFIG
import os

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg://{os.environ['DB_USER']}:"
    f"{os.environ['DB_PASSWORD']}@{os.environ['DB_HOST']}:"
    f"{os.environ['DB_PORT']}/{os.environ['DB_NAME']}"
)
db = SQLAlchemy(app)
with app.app_context():
    SQLAlchemyInstrumentor().instrument(engine=db.engine)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    security_answer = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(30), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

    
    
    




@app.route('/')
def homePage():
    return render_template('homepage.html')

# @app.route('/signIn')
# def loginPage():
#     return render_template('loginPage.html')

@app.route("/signIn", methods=["GET", "POST"])
def loginPage():

    if request.method == "POST":

        username = request.form["username"].lower()
        password = request.form["password"]

        user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar()

    

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["username"] = user.username
            logger.info(
                "Login successful",
                extra={"request_name": "login_success"}
            )

            return redirect(url_for("loggedIn"))
        logger.warning(
            "Invalid credentials",
            extra={
                "request_name": username,
                "failure_reason": "invalid_credentials",
                "nginx_request_id": request.headers.get("X-Request-ID"),
            }
        )


        flash("Invalid username or password.")
        return render_template("loginPage.html"), 401

     

    return render_template("loginPage.html")

@app.route('/createUser', methods=["GET","POST"])
def createUser():
    if request.method == "POST":
        name = request.form["username"].lower()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        security_answer = request.form["security_answer"].lower()

        user = User(
            username=name,
            email=email,
            password=hashed_password,
            security_answer=security_answer
        )

        db.session.add(user)
        db.session.commit()
        logger.info("Request received", extra={"request_name": name})
        flash(f"User '{name}' created successfully!")
        return redirect(url_for("loginPage"))

    return render_template('createUserPage.html')

@app.route('/forgotPassword')
def forgotPassword():
    return render_template('forgot-password.html')

@app.route("/passwordRecovery", methods=["POST"])
def passwordRecovery():

    if "new_password" in request.form:

        username = request.form["username"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            return "Passwords do not match"

        user = db.session.execute(
            db.select(User).where(User.username == username)
        ).scalar()

        user.password = generate_password_hash(new_password)

        db.session.commit()

        flash("Password updated successfully!")
        return redirect(url_for("loginPage"))

    username = request.form["username"]
    answer = request.form["security_answer"]

    user = db.session.execute(
        db.select(User).where(User.username == username)
    ).scalar()

    if user and user.security_answer == answer:
        is_valid = True
    else:
        is_valid = False

    return render_template(
        "passwordRecovery.html",
        is_valid=is_valid,
        username=username
    )


@app.route("/loggedIn")
def loggedIn():

    if "user_id" not in session:
        return redirect(url_for("loginPage"))

    username = session["username"]

    products = db.session.execute(
        db.select(Product)
    ).scalars().all()

    return render_template(
        "loggedIn.html",
        username=username,
        products=products
    )

@app.route("/addToCart", methods=["POST"])
def addToCart():

    if "user_id" not in session:
        return redirect(url_for("loginPage"))

    product_id = int(request.form["product_id"])    

    cart_item = db.session.execute(
        db.select(Cart).where(
            Cart.user_id == session["user_id"],
            Cart.product_id == product_id
        )
    ).scalar()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(
            user_id=session["user_id"],
            product_id=product_id,
            quantity=1
        )
        db.session.add(cart_item)

    db.session.commit()

    flash("Product added to cart successfully!")

    return redirect(url_for("loggedIn"))

@app.route("/cart")
def cart():

    if "user_id" not in session:
        return redirect(url_for("loginPage"))

    cart_items = db.session.execute(
        db.select(Cart, Product)
        .join(Product, Cart.product_id == Product.id)
        .where(Cart.user_id == session["user_id"])
    ).all()

    return render_template(
        "cart.html",
        cart_items=cart_items
    )
@app.route("/updateCart/<int:cart_id>/<action>", methods=["POST"])
def updateCart(cart_id, action):

    cart_item = db.session.get(Cart, cart_id)

    if not cart_item or cart_item.user_id != session["user_id"]:
        return redirect(url_for("cart"))

    if action == "increase":
        cart_item.quantity += 1

    elif action == "decrease":
        cart_item.quantity -= 1

        if cart_item.quantity <= 0:
            db.session.delete(cart_item)

    db.session.commit()

    return redirect(url_for("cart"))

@app.route("/deleteCart/<int:cart_id>", methods=["POST"])
def deleteCart(cart_id):

    cart_item = db.session.get(Cart, cart_id)

    if cart_item and cart_item.user_id == session["user_id"]:
        db.session.delete(cart_item)
        db.session.commit()

    return redirect(url_for("cart"))

@app.route("/submitOrder", methods=["POST"])
def submitOrder():

    if "user_id" not in session:
        return redirect(url_for("loginPage"))

    cart_items = db.session.execute(
        db.select(Cart, Product)
        .join(Product, Cart.product_id == Product.id)
        .where(Cart.user_id == session["user_id"])
    ).all()

    total_price = sum(
        product.price * cart.quantity
        for cart, product in cart_items
    )

    order_number = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    order = Order(
        order_number=order_number,
        user_id=session["user_id"],
        total_price=total_price
    )

    db.session.add(order)

    for cart, product in cart_items:
        db.session.delete(cart)

    db.session.commit()

    return redirect(
    url_for(
        "orderSubmitted",
        order_number=order_number
    )
)

@app.route("/orderSubmitted")
def orderSubmitted():

    if "user_id" not in session:
        return redirect(url_for("loginPage"))

    order_number = request.args.get("order_number")

    return render_template(
        "orderSubmitted.html",
        order_number=order_number
    )

@app.route("/myOrders")
def myOrders():

    if "user_id" not in session:
        return redirect(url_for("loginPage"))

    orders = db.session.execute(
        db.select(Order)
        .where(Order.user_id == session["user_id"])
        .order_by(Order.id.desc())
    ).scalars().all()

    username = session["username"]

    return render_template(
        "myOrders.html",
        orders=orders,
        username=username
    )

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("loginPage"))

if __name__ == "__main__":
    app.run(debug=True)
