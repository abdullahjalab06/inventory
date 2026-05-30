import os
from inventory import add_product, db_add_stock, show_products, register_user

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_prod():

    if request.method == "POST":

        productname = request.form["productname"]

        quantity = request.form["quantity"]

        price = request.form["price"]

        add_product(productname, quantity, price)

        return "Product Added"

    return render_template("add-product.html")


@app.route("/add_new_stock")
def show_add_stock():
    products = show_products()
    return render_template("update-product.html", products=products)


@app.route("/add_new_stock/<int:id>", methods=["POST"])
def add_new_stock(id):
    if request.method=="POST":
        quantity = int(request.form["quantity"])

        db_add_stock(id, quantity)

        return redirect(url_for("show_add_stock"))


@app.route("/register", methods=["GET", "POST"])
def create_user():
    if request.method=="POST":
        username = request.form["username"]
        email = request.form["email"]
        password=request.form["password"]

        register_user(username, email,password)
        return render_template("index.html")
    return render_template("registers.html")


@app.route("/all_product", methods=["GET", "POST"])
def all_products():

    the_products = show_products()

    return render_template("all-products.html", the_products=the_products)



if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )