from flask import Flask, send_from_directory, render_template, jsonify, request, redirect, url_for, flash, session
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for security

# Hardcoded user credentials
users = {
    "admin": "decon123"
}

# Dictionary to store data received from Raspberry Pis
pi_data = {}

# Home page to render the login form
@app.route('/')
def home():
    return render_template('login.html')

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username] == password:
        session['username'] = username
        return redirect(url_for('protected'))  # Redirect to the protected page
    else:
        flash('Invalid credentials. Please try again.')
        return redirect(url_for('home'))

# Protected route to render the main application
@app.route('/protected')
def protected():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return redirect(url_for('home'))

# Endpoint to receive data from Raspberry Pis
@app.route('/send_data', methods=['POST'])
def receive_data():
    data = request.json
    pi_id = data.get('pi_id')
    product_count = data.get('product_count')
    not_ok_count = data.get('not_ok_count')
    shift = data.get('shift')

    # Store the data received from the Raspberry Pi
    pi_data[pi_id] = {
        'product_count': product_count,
        'not_ok_count': not_ok_count,
        'shift': shift
    }

    # Send a confirmation message back to the Raspberry Pi
    return jsonify({'status': f'Data received from {pi_id}'})

# Endpoint to retrieve the stored data
@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify(pi_data)

# Endpoint to download Excel file
@app.route('/download_data', methods=['GET'])
def download_data():
    # Create a DataFrame from the stored data
    df = pd.DataFrame.from_dict(pi_data, orient='index')

    # Define the path to save the Excel file
    file_path = 'raspberry_pi_data.xlsx'
    
    # Save DataFrame to an Excel file
    df.to_excel(file_path, index=True)  # Include index (PI ID) as a column

    # Send the file to the client
    return send_from_directory(os.getcwd(), file_path, as_attachment=True)

# Endpoint to serve images from the Images directory
@app.route('/Images/<path:filename>')
def serve_image(filename):
    return send_from_directory('Images', filename)

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
