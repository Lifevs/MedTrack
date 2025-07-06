from flask import Flask, render_template, request, redirect, url_for, session, flash
import boto3
import uuid

app = Flask(__name__)
app.secret_key = 'pzegzzxDEYSpBzZdvtgbmXCbMkVKv3T6K6Ti10ZI'

# AWS Configuration
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')  # Change if needed
sns = boto3.client('sns', region_name='ap-south-1')
sns_topic_arn = 'arn:aws:sns:ap-south-1:533267340399:medTrack.fifo'  # Replace with actual ARN

# DynamoDB Tables
user_table = dynamodb.Table('Users')
doctor_table = dynamodb.Table('Doctors')
appointment_table = dynamodb.Table('Appointments')

# Routes
@app.route('/')
def home():
    return render_template('index.html')

# ------------------ AUTH ------------------
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
            print(f"Error: {str(e)}", "danger")
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

# ------------------ DASHBOARD ------------------
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# ------------------ DOCTORS ------------------
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

# ------------------ APPOINTMENTS ------------------
@app.route('/book', methods=['GET', 'POST'])
def book_appointment():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        doctor_id = request.form['doctor_id']
        date = request.form['date']
        time = request.form['time']
        symptoms = request.form['symptoms']
        appointment_id = str(uuid.uuid4())
        user_email = session['user']

        try:
            # Save to DynamoDB
            appointment_table.put_item(Item={
                'appointment_id': appointment_id,
                'user_email': user_email,
                'doctor_id': doctor_id,
                'date': date,
                'time': time,
                'symptoms': symptoms
            })

            # Get doctor name
            doctor_response = doctor_table.get_item(Key={'doctor_id': doctor_id})
            doctor = doctor_response.get('Item', {})
            doctor_name = doctor.get('name', 'Unknown')

            # Send SNS notification
            message = f"Appointment confirmed with Dr. {doctor_name} on {date} at {time}.\nReason: {symptoms}"
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

    # GET: load all doctors
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
        # Get all appointments
        response = appointment_table.scan()
        all_appointments = response.get('Items', [])
        user_appointments = [appt for appt in all_appointments if appt.get('user_email') == user_email]

        # Fetch all doctors once
        doctor_response = doctor_table.scan()
        all_doctors = doctor_response.get('Items', [])

        # Attach doctor info to each appointment
        for appt in user_appointments:
            matching_doc = next((doc for doc in all_doctors if doc.get('doctor_id') == appt.get('doctor_id')), {})
            appt['doctor_name'] = matching_doc.get('name', 'Unknown')
            appt['speciality'] = matching_doc.get('speciality', 'N/A')

        return render_template('appointments.html', appointments=user_appointments)

    except Exception as e:
        print(f"Error loading appointments: {str(e)}")
        flash(f"Error loading appointments: {str(e)}", "danger")
        return redirect(url_for('dashboard'))


# ------------------ Run Server ------------------
if __name__ == '__main__':
    app.run(debug=True)
