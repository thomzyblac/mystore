import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Configurations
DATABASE = 'database.db'
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 📞 Change this to your real WhatsApp number!
WHATSAPP_NUMBER = "+2349035442963" 

def init_db():
    """Creates the database table if it doesn't exist and automatically inserts starter goods."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create the products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT NOT NULL
        )
    ''')
    
    # Check if we already have products. If not, insert some starters!
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)",
                       ("Cool Sneakers", "$50.00", "Super comfortable running shoes.", "sneakers.jpg"))
        cursor.execute("INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)",
                       ("Vintage Watch", "$120.00", "A classic timepiece that never goes out of style.", "watch.jpg"))
        cursor.execute("INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)",
                       ("Wireless Headphones", "$85.00", "Crystal clear sound with deep bass.", "headphones.jpg"))
        conn.commit()
        
    conn.close()

# Initialize the database immediately when the server spins up
init_db()

@app.route('/')
def home():
    """Fetches all items from our database and displays them on the storefront."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Dict-like access for our HTML template
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    my_goods = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=my_goods, phone=WHATSAPP_NUMBER)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Handles displaying the admin form and saving newly uploaded products."""
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        
        image_file = request.files['image']
        if image_file:
            filename = image_file.filename
            # Save the physical image file to our static directory
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # Save the data pathway to our SQLite database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)",
                           (name, price, description, filename))
            conn.commit()
            conn.close()
            
            return redirect(url_for('home'))
            
    return render_template('admin.html')


if __name__ == '__main__':
    # Guarantee our upload folder exists locally
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
