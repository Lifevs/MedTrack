# 🩺 HealthCare Booking System

A modern, responsive Healthcare Appointment Booking web app built using **Flask**, **AWS DynamoDB**, and **SNS**. Patients can register, login, browse available doctors, book appointments, and receive confirmation alerts via email.

![HealthCare UI](https://img.shields.io/badge/Flask-2.3-blue?logo=flask) ![AWS](https://img.shields.io/badge/AWS-DynamoDB%20%2F%20SNS-orange?logo=amazonaws) ![Responsive](https://img.shields.io/badge/UI-Responsive-green)

---

## 🌟 Features

- ✅ User Registration, Login, and Logout
- 🩺 Doctor Listings with Specializations
- 📅 Book Appointments with Available Doctors
- 📧 Email Notifications via AWS SNS
- 🧾 View Your Past Appointments
- 🔒 Role-Based Access (Admin, Patient, Doctor - Extendable)
- 💠 Beautiful Gradient UI & Responsive Design

---

## 🛠️ Tech Stack

| Layer         | Technology                  |
|---------------|------------------------------|
| Frontend      | HTML5, CSS3 (with gradients), Jinja2 |
| Backend       | Python, Flask                |
| Database      | AWS DynamoDB (NoSQL)         |
| Notifications | AWS SNS (Simple Notification Service) |
| Hosting       | Flask local server / EC2-ready |

---

## 🎥 Demo Video
[![Watch the Demo](assets/demo-thumbnail.png)](https://drive.google.com/file/d/1m0nCIB16Wc3wr9F4SOUdD6Tb099AiYop/view?usp=sharing)

## 📁 Folder Structure

healthcare-app/
│
├── templates/ # HTML templates
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── dashboard.html
│ ├── doctors.html
│ ├── book_appointment.html
│ └── appointments.html
│
├── static/
│ └── style.css # Gradient theme + responsive UI
│
├── app.py # Main Flask app
├── requirements.txt
└── README.md

🧾 DynamoDB Tables Used

Table Name	Partition Key
Users	email (string)
Doctors	name (string)
Appointments	appointment_id (string)
You can extend this with composite keys (doctor_id, email, etc.) for optimization.
📸 Screenshots

Home Page	Doctor List	Book Appointment	Appointments
📌 Future Enhancements

 Role-based dashboards (Doctor, Admin)
 Doctor-side appointment management
 Password hashing (bcrypt)
 Calendar availability slots
 Appointment rescheduling/cancelation
 AWS Cognito for verified user management
 Deployed version with CI/CD
🧪 Test Accounts

You can create dummy users during registration.
Coming soon: Seed scripts for test data and sample doctors.

📄 License

This project is licensed under the MIT License.

🙌 Contributing

Pull requests are welcome! If you'd like to suggest a feature or report a bug, please open an issue.
