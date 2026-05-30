import os
from functools import wraps

from inventory import (
    add_product, db_add_stock, show_products,
    register_user, sell_product, login_user,
    search_products, get_all_sales, get_recent_sales,
    get_dashboard_stats
)

from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "mustodai_secret_2024_xK9"


# ==================== حماية المسارات ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("يجب تسجيل الدخول أولاً", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ==================== لوحة التحكم (الصفحة الرئيسية) ====================

@app.route("/")
@login_required
def home():
    stats = get_dashboard_stats()
    recent_sales = get_recent_sales(5)
    return render_template("index.html", stats=stats, recent_sales=recent_sales)


# ==================== المنتجات ====================

@app.route("/add", methods=["GET", "POST"])
@login_required
def add_prod():
    if request.method == "POST":
        productname = request.form["productname"].strip()
        quantity = int(request.form["quantity"])
        price = float(request.form["price"])

        if not productname:
            flash("اسم المنتج لا يمكن أن يكون فارغاً", "danger")
            return render_template("add-product.html")
        if quantity < 0:
            flash("الكمية لا يمكن أن تكون سالبة", "danger")
            return render_template("add-product.html")
        if price < 0:
            flash("السعر لا يمكن أن يكون سالباً", "danger")
            return render_template("add-product.html")

        add_product(productname, quantity, price)
        flash(f"تمت إضافة '{productname}' بنجاح", "success")
        return redirect(url_for("home"))

    return render_template("add-product.html")


@app.route("/all_product")
@login_required
def all_products():
    the_products = show_products()
    return render_template("all-products.html", the_products=the_products)


@app.route("/add_new_stock")
@login_required
def show_add_stock():
    products = show_products()
    return render_template("update-product.html", products=products)


@app.route("/add_new_stock/<int:id>", methods=["POST"])
@login_required
def add_new_stock(id):
    quantity = int(request.form["quantity"])
    if quantity <= 0:
        flash("يجب أن تكون الكمية أكبر من صفر", "danger")
        return redirect(url_for("show_add_stock"))
    db_add_stock(id, quantity)
    flash(f"تم إضافة {quantity} للمخزون بنجاح", "success")
    return redirect(url_for("show_add_stock"))


@app.route("/sell_product/<int:id>", methods=["POST"])
@login_required
def sell_product_route(id):
    amount = int(request.form["amount"])
    success, message = sell_product(id, amount)
    flash(message, "success" if success else "danger")
    return redirect(url_for("show_add_stock"))


# ==================== البحث ====================

@app.route("/search")
@login_required
def search():
    query = request.args.get("q", "").strip()
    results = search_products(query) if query else []
    return render_template("search.html", results=results, query=query)


# ==================== سجل المبيعات ====================

@app.route("/sales")
@login_required
def sales_history():
    sales = get_all_sales()
    return render_template("sales.html", sales=sales)


# ==================== تسجيل الدخول والخروج ====================

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        success, user, message = login_user(email, password)
        if success:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"أهلاً {user['username']}! 👋", "success")
            return redirect(url_for("home"))
        else:
            flash(message, "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def create_user():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        if len(password) < 6:
            flash("كلمة المرور يجب أن تكون 6 أحرف على الأقل", "danger")
            return render_template("registers.html")

        success, message = register_user(username, email, password)
        if success:
            flash(message + " — يمكنك تسجيل الدخول الآن", "success")
            return redirect(url_for("login"))
        else:
            flash(message, "danger")

    return render_template("registers.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("تم تسجيل الخروج بنجاح", "info")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
