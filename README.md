
# 🚍 AI-Based Real-Time Bus Crowd Prediction System

![Python](https://img.shields.io/badge/Python-3.10-blue)
![AI](https://img.shields.io/badge/AI-Machine%20Learning-green)
![Status](https://img.shields.io/badge/Project-Final%20Year%20Major%20Project-orange)
![License](https://img.shields.io/badge/License-MIT-purple)
![Contributions](https://img.shields.io/badge/Contributions-Welcome-brightgreen)

> An **AI-powered intelligent transportation system** that predicts real-time bus crowd levels using **conductor ticket data** and helps passengers make smarter travel decisions.

Developed as a **Final Year Major Project** at **Nitte Meenakshi Institute of Technology (VTU)**. 

---

# 📌 Table of Contents

* Project Overview
* Key Features
* Innovation
* System Architecture
* Tech Stack
* Demo
* Folder Structure
* Installation Guide
* Usage
* Evaluation Metrics
* Future Enhancements
* Team

---

# 📖 Project Overview

Public transportation systems often suffer from **overcrowded buses and lack of real-time seat availability information**. Passengers usually rely on guesswork when deciding whether to board a bus.

This project introduces a **smart AI-driven system** that predicts **bus crowd levels in real time** using conductor ticket selling data and bus capacity information.

Passengers can view:

* 📍 Live bus location
* 🪑 Seat availability
* 📊 Crowd level prediction

This enables passengers to **choose less crowded buses and improve their commuting experience**. 

---

# ✨ Key Features

🚍 **Real-Time Bus Tracking**
GPS-based tracking shows live bus locations.

🪑 **Seat Availability Prediction**
Uses ticket sales data to estimate occupancy.

📊 **Crowd Level Classification**

* Seats Available
* Moderate Crowd
* Bus Full

📱 **Passenger Information Interface**
Mobile/web interface showing bus status.

🔔 **Smart Notifications**
Passengers receive alerts when a bus with available seats approaches their stop.

---

# 💡 Core Innovation

Most existing systems rely on expensive hardware such as:

* CCTV cameras
* Infrared sensors
* Passenger counting devices

Our system instead uses **existing conductor ticket selling data**, making it:

✔ Cost-efficient
✔ Easy to deploy
✔ Scalable for entire cities

This significantly reduces infrastructure costs while maintaining accurate crowd predictions. 

---

# 🏗️ System Architecture

```
             +---------------------------+
             | Conductor Ticket Machine  |
             +-------------+-------------+
                           |
                           v
                 +------------------+
                 | Data Collection  |
                 |      API         |
                 +---------+--------+
                           |
                           v
                +---------------------+
                |   Cloud Server /    |
                |      Database       |
                +---------+-----------+
                          |
                          v
               +----------------------+
               | Crowd Prediction AI  |
               |  Classification      |
               +----------+-----------+
                          |
                          v
               +----------------------+
               |  Mobile / Web App    |
               +----------+-----------+
                          |
                          v
               +----------------------+
               | Passenger Alerts &   |
               | Seat Availability    |
               +----------------------+
```

---

# 🧠 Crowd Classification Logic

```
if occupancy < 80%:
    status = "Seats Available"

elif occupancy between 80% and 95%:
    status = "Moderate Crowd"

else:
    status = "Bus Full"
```

Future versions may use **machine learning prediction models** for forecasting crowd levels.

---

# 🛠️ Tech Stack

### Artificial Intelligence

* Python
* Machine Learning

### Backend

* Node.js / Flask
* REST APIs

### Database

* PostgreSQL / Firebase

### Frontend

* React
* Web / Mobile Interface

### Infrastructure

* Cloud Server
* GPS Integration

---

# 🎥 Demo

*(Add demo screenshots or GIFs here)*

Example sections you can add:

```
docs/demo1.gif
docs/demo2.gif
```

Example:

* Live Bus Tracking
* Seat Availability Display
* Passenger Notification

---

# 📂 Project Folder Structure

```
bus-crowd-prediction/
│
├── backend/
│   ├── api
│   ├── server
│   └── prediction_model
│
├── frontend/
│   ├── components
│   ├── pages
│   └── assets
│
├── data/
│   └── ticket_data_samples
│
├── docs/
│   ├── architecture.png
│   └── demo.gif
│
├── models/
│   └── crowd_classifier.py
│
├── README.md
└── requirements.txt
```

---

# ⚙️ Installation Guide

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/bus-crowd-prediction.git
```

---

### 2️⃣ Navigate to project directory

```bash
cd bus-crowd-prediction
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run backend server

```bash
python app.py
```

---

### 5️⃣ Start frontend

```bash
npm install
npm start
```

---

# ▶️ Usage

1️⃣ Conductors sell tickets using ticket machines.
2️⃣ Ticket data is sent to the cloud server.
3️⃣ AI model calculates current occupancy.
4️⃣ System classifies crowd level.
5️⃣ Passengers see **live bus crowd status and notifications**.

---

# 📊 Evaluation Metrics

The system performance is evaluated using:

| Metric        | Description                           |
| ------------- | ------------------------------------- |
| Accuracy      | Correct occupancy predictions         |
| Precision     | Correct seat availability alerts      |
| Recall        | True detection of available seats     |
| F1 Score      | Balance of precision and recall       |
| Response Time | Time from ticket sale to notification |

Expected performance:

✔ **Accuracy:** ~90%
✔ **Response Time:** < 5 seconds 

---

# 🚀 Future Enhancements

* Deep Learning crowd prediction
* Historical travel pattern analysis
* Smart route recommendations
* Integration with **city transport apps**
* Smart city transportation analytics

---

# 👨‍💻 Project Team

**Department of Artificial Intelligence & Machine Learning**
Nitte Meenakshi Institute of Technology (VTU)

Team Members:

* **Abhishek J C**
* **Diya Sharma**
* **Manishika Puhan**
* **Shrianjanchari Tadury**

Guide:

**Mrs. Divyaraj G N**
Assistant Professor, AIML Department 

---

# 🤝 Contributing

Contributions are welcome!

Steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Submit a pull request

---

# ⭐ Support

If you found this project useful:

⭐ Star the repository
🍴 Fork the project
📢 Share it with others

