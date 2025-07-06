import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash, session
import boto3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('secret_key')

# AWS Configuration
aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
aws_region = os.getenv('AWS_DEFAULT_REGION')
sns_topic_arn = os.getenv('SNS_TOPIC_ARN')

# AWS Clients
dynamodb = boto3.resource(
    'dynamodb',
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

sns = boto3.client(
    'sns',
    region_name=aws_region,
    aws_access_key_id=aws_access_key,
    aws_secret_access_key=aws_secret_key
)

# DynamoDB Tables
user_table = dynamodb.Table('Users')
doctor_table = dynamodb.Table('Doctors')  # 'name' is partition key
appointment_table = dynamodb.Table('Appointments')  # 'appointment_id' is partition key

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user_table.put_item(Item={'email': email, 'password': password})
            flash("Registered successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error: {str(e)}")
            flash("Registration failed.", "danger")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            response = user_table.get_item(Key={'email': email})
            user = response.get('Item')
            if user and user['password'] == password:
                session['user'] = email
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials!", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/doctors')
def view_doctors():
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        response = doctor_table.scan()
        doctors = response.get('Items', [])
        return render_template('doctors.html', doctors=doctors)
    except Exception as e:
        flash(f"Error fetching doctors: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/book', methods=['GET', 'POST'])
def book_appointment():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_name = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']
        symptoms = request.form['symptoms']
        appointment_id = str(uuid.uuid4())
        user_email = session['user']

        try:
            appointment_table.put_item(Item={
                'appointment_id': appointment_id,
                'user_email': user_email,
                'doctor_id': doctor_name,
                'date': date,
                'time': time,
                'symptoms': symptoms
            })

            doctor_response = doctor_table.get_item(Key={'name': doctor_name})
            doctor = doctor_response.get('Item', {})
            doctor_display = doctor.get('name', 'Unknown')

            message = f"Appointment confirmed with Dr. {doctor_display} on {date} at {time}.\nReason: {symptoms}"
            sns.publish(
                TopicArn=sns_topic_arn,
                Message=message,
                Subject='Appointment Booked'
            )

            flash("Appointment booked successfully!", "success")
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f"Error booking appointment: {str(e)}", "danger")
            return redirect(url_for('dashboard'))

    try:
        response = doctor_table.scan()
        doctors = response.get('Items', [])
        return render_template('book_appointment.html', doctors=doctors)
    except Exception as e:
        flash(f"Error loading doctors: {str(e)}", "danger")
        return redirect(url_for('dashboard'))

@app.route('/appointments')
def view_appointments():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_email = session['user']
    try:
        response = appointment_table.scan()
        all_appointments = response.get('Items', [])
        user_appointments = [appt for appt in all_appointments if appt.get('user_email') == user_email]

        for appt in user_appointments:
            doc = doctor_table.get_item(Key={'name': appt['doctor_id']}).get('Item', {})
            appt['doctor_name'] = doc.get('name', 'Unknown')
            appt['speciality'] = doc.get('speciality', 'N/A')

        return render_template('appointments.html', appointments=user_appointments)

    except Exception as e:
        print(f"Error loading appointments: {str(e)}")
        flash("Could not load appointments.", "danger")
        return redirect(url_for('dashboard'))

# ------------------ Run Server ------------------
if __name__ == '__main__':
    app.run(debug=True)
