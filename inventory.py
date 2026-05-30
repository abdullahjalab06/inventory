import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


# ==================== المنتجات ====================

def add_product(productname, quantity, price):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (productname, quantity, price)
        VALUES (?, ?, ?)
    """, (productname, quantity, price))
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
    """بيع منتج: تخفيض الكمية وتسجيل البيع في سجل المبيعات"""
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
    product = cursor.fetchone()

    if product is None:
        conn.close()
        return False, "المنتج غير موجود"

    current_quantity = product["quantity"]

    if amount <= 0:
        conn.close()
        return False, "يجب أن تكون الكمية أكبر من صفر"

    if current_quantity < amount:
        conn.close()
        return False, f"الكمية المطلوبة ({amount}) أكبر من المخزون الحالي ({current_quantity})"

    new_quantity = current_quantity - amount
    total_amount = amount * product["price"]

    # تحديث كمية المنتج
    cursor.execute("""
        UPDATE products SET quantity = ? WHERE id = ?
    """, (new_quantity, id))

    # تسجيل البيع في جدول sales
    cursor.execute("""
        INSERT INTO sales (product_id, productname, quantity_sold, price_at_sale, total_amount)
        VALUES (?, ?, ?, ?, ?)
    """, (id, product["productname"], amount, product["price"], total_amount))

    conn.commit()
    conn.close()
    return True, f"تم بيع {amount} قطعة بمبلغ {total_amount:.2f}"


def show_products():
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products ORDER BY productname")
    products = cursor.fetchall()
    conn.close()
    return products


def search_products(query):
    """البحث عن منتج بالاسم — يدعم البحث الجزئي"""
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products
        WHERE productname LIKE ?
        ORDER BY productname
    """, ('%' + query + '%',))
    results = cursor.fetchall()
    conn.close()
    return results


def get_product(id):
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def total_inventory_value():
    """إجمالي قيمة المخزون (الكمية × السعر)"""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT quantity, price FROM products")
    rows = cursor.fetchall()
    total = sum(q * p for q, p in rows)
    conn.close()
    return total


# ==================== سجل المبيعات ====================

def get_all_sales():
    """جلب جميع سجلات المبيعات مرتبة من الأحدث للأقدم"""
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sales
        ORDER BY sold_at DESC
    """)
    sales = cursor.fetchall()
    conn.close()
    return sales


def get_recent_sales(limit=5):
    """جلب آخر N عمليات بيع للوحة التحكم"""
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM sales
        ORDER BY sold_at DESC
        LIMIT ?
    """, (limit,))
    sales = cursor.fetchall()
    conn.close()
    return sales


def get_total_sales_count():
    """عدد عمليات البيع الكلي"""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM sales")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_sales_revenue():
    """إجمالي الإيرادات من المبيعات"""
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(total_amount) FROM sales")
    result = cursor.fetchone()[0]
    conn.close()
    return result or 0


# ==================== إحصائيات لوحة التحكم ====================

def get_dashboard_stats():
    """جلب جميع إحصائيات لوحة التحكم دفعة واحدة"""
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # عدد المنتجات
    cursor.execute("SELECT COUNT(*) as count FROM products")
    total_products = cursor.fetchone()["count"]

    # إجمالي الكميات في المخزون
    cursor.execute("SELECT SUM(quantity) as total FROM products")
    result = cursor.fetchone()["total"]
    total_quantity = result if result else 0

    # المنتجات منخفضة المخزون (أقل من 10)
    LOW_STOCK_THRESHOLD = 10
    cursor.execute("SELECT COUNT(*) as count FROM products WHERE quantity < ?", (LOW_STOCK_THRESHOLD,))
    low_stock_count = cursor.fetchone()["count"]

    # قائمة المنتجات منخفضة المخزون
    cursor.execute("""
        SELECT * FROM products WHERE quantity < ?
        ORDER BY quantity ASC
    """, (LOW_STOCK_THRESHOLD,))
    low_stock_products = cursor.fetchall()

    # عدد عمليات البيع
    cursor.execute("SELECT COUNT(*) as count FROM sales")
    total_sales = cursor.fetchone()["count"]

    # إجمالي الإيرادات
    cursor.execute("SELECT SUM(total_amount) as total FROM sales")
    revenue_result = cursor.fetchone()["total"]
    total_revenue = revenue_result if revenue_result else 0

    # قيمة المخزون
    cursor.execute("SELECT SUM(quantity * price) as val FROM products")
    val_result = cursor.fetchone()["val"]
    inventory_value = val_result if val_result else 0

    conn.close()

    return {
        "total_products": total_products,
        "total_quantity": total_quantity,
        "low_stock_count": low_stock_count,
        "low_stock_products": low_stock_products,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "inventory_value": inventory_value,
        "low_stock_threshold": LOW_STOCK_THRESHOLD
    }


# ==================== المستخدمون ====================

def register_user(username, email, password):
    conn = sqlite3.connect("inventory.db")
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (?, ?, ?)
        """, (username, email, hashed_password))
        conn.commit()
        conn.close()
        return True, "تم التسجيل بنجاح"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "البريد الإلكتروني مستخدم مسبقاً"


def login_user(email, password):
    conn = sqlite3.connect("inventory.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        return False, None, "البريد الإلكتروني غير موجود"

    if check_password_hash(user["password"], password):
        return True, dict(user), "تم تسجيل الدخول بنجاح"
    else:
        return False, None, "كلمة المرور غير صحيحة"
