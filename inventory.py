import sqlite3


def add_product(productname, quantity, price):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO products (productname, quantity, price)
                   VALUES (?, ?, ?)
            
    """,(productname, quantity, price))
    conn.commit()
    conn.close()


def db_add_stock(id, quantity):

    conn = sqlite3.connect("inventory.db")

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET quantity = quantity + ?
        WHERE id = ?
    """, (quantity, id))

    conn.commit()

    conn.close()

def sell_product(id, amount):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM products WHERE id = ?", (id,))
    product = cursor.fetchone()

    if product is None:
        return "Product Not Found!"

    current_quantity = product[0]

    if current_quantity < amount:
        return "Not enough stock!"

    new_quantity = current_quantity - amount

    cursor.execute("""
        UPDATE products
        SET quantity = ?
        WHERE id = ?
    """, (new_quantity, id))

    conn.commit()
    conn.close()

    print("Updated rows:", cursor.rowcount)


def show_products():
    
    conn = sqlite3.connect("inventory.db")

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products")

    products = cursor.fetchall()

    conn.close()

    return products

def get_product(productname):
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE productname = ?", (productname,))
    row = cursor.fetchone()

    conn.close()
    if row is None:
        return None
    return dict(row)


def low_stock_alert():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # threshold من المستخدم
    less_stock = int(input("Enter low stock limit: "))

    # جلب كل المنتجات
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    conn.close()

    # قائمة للمنتجات اللي تحت الحد
    low_products = []

    # فحص كل منتج
    for product in products:
        if product["quantity"] < less_stock:
            low_products.append(product)

    # إذا ما في شي منخفض
    if len(low_products) == 0:
        print("All products are OK")
    else:
        for p in low_products:
            print(p["productname"], "-", p["quantity"])

def total_dolar():  # to add the full prices of products
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("SELECT quantity, price FROM products")
    rows = cursor.fetchall()

    total = sum(quantity * price for quantity, price in rows)

    conn.close()
    return total

def register_user(username, email, password):

    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    """, (username, email, password))

    conn.commit()
    conn.close()
