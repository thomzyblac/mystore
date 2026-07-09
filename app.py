import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Configurations
DATABASE = 'database.db'
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
WHATSAPP_NUMBER = "YOUR_PHONE_NUMBER"  # Double check this is your number!

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            description TEXT NOT NULL,
            image TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    my_goods = cursor.fetchall()
    conn.close()
    return render_template('index.html', products=my_goods, phone=WHATSAPP_NUMBER)


# 🔒 NEW: Admin Route to handle adding products
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # 1. Grab text data from form
        name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        
        # 2. Grab and save the uploaded image file
        image_file = request.files['image']
        if image_file:
            filename = image_file.filename
            # Save the file into static/images/
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            # 3. Insert into the database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (name, price, description, image) VALUES (?, ?, ?, ?)",
                           (name, price, description, filename))
            conn.commit()
            conn.close()
            
            # Redirect to homepage to see your new product!
            return redirect(url_for('home'))
            
    # If it's a GET request, just show the admin form page
    return render_template('admin.html')


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)