from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


# Database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345678',  # replace with your MySQL root password
        database='banking_system'
    )
    return conn
def update_names():
    # Connect to the database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='12345678',  # replace with your MySQL root password
        database='banking_system'
    )

    # Mapping of original names to Indian names
    name_mapping = {
        "Alice": "Akash",
        "Bob": "Bharti",
        "Charlie": "Candy",
        "David": "Gireesh",
        "Eve": "Harshil",
        "Frank": "Ishaan",
        "Grace": "Karishma",
        "Hank": "Lavya",
        "Ivy": "Manish",
        "Jack": "Purohit"
    }

    # Prepare and execute UPDATE queries for each name
    for original_name, indian_name in name_mapping.items():
        update_query = "UPDATE customers SET name = %s WHERE name = %s"
        cursor = conn.cursor()
        cursor.execute(update_query, (indian_name, original_name))
        conn.commit()
        cursor.close()

    # Close the database connection
    conn.close()

# Route to trigger the update process
@app.route('/update_names')
def trigger_update_names():
    update_names()  # Call the function to update names
    return redirect(url_for('view_customers'))  

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/customers')
def view_customers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM customers')
    customers = cursor.fetchall()
    conn.close()
    return render_template('customers.html', customers=customers)

@app.route('/customer/<int:id>')
def view_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM customers WHERE id = %s', (id,))
    customer = cursor.fetchone()
    cursor.execute('SELECT * FROM customers WHERE id != %s', (id,))
    customers = cursor.fetchall()
    conn.close()
    return render_template('customer.html', customer=customer, customers=customers)

@app.route('/transfer', methods=['POST'])
def transfer_money():
    sender_id = request.form['sender_id']
    receiver_id = request.form['receiver_id']
    amount = request.form['amount']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT current_balance FROM customers WHERE id = %s', (sender_id,))
    sender_balance = cursor.fetchone()[0]

    if sender_balance >= float(amount):
        cursor.execute('UPDATE customers SET current_balance = current_balance - %s WHERE id = %s', (amount, sender_id))
        cursor.execute('UPDATE customers SET current_balance = current_balance + %s WHERE id = %s', (amount, receiver_id))
        cursor.execute('INSERT INTO transfers (sender_id, receiver_id, amount) VALUES (%s, %s, %s)', (sender_id, receiver_id, amount))
        conn.commit()

    conn.close()
    return redirect(url_for('view_customers'))

if __name__ == '__main__':
    app.run(debug=True)
