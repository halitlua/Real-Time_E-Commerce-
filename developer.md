# Parallel Fulfillment System

## Project Overview

The Parallel Fulfillment System is a web-based order processing application developed using Python, Flask, SQLite, HTML, CSS, and JavaScript.

The system simulates a real-world fulfillment center where customer orders are processed concurrently by multiple worker threads. Orders progress through several fulfillment stages, including payment validation, inventory checking, shipping label generation, packaging, and completion.

The project demonstrates:

* Parallel Computing
* Multi-threading
* Queue-based Processing
* Real-Time Monitoring
* Database Integration
* Web Application Development

---

# System Architecture

Frontend

* Customer Portal
* Admin Dashboard
* HTML
* Tailwind CSS
* JavaScript

Backend

* Flask
* Python

Database

* SQLite

Processing Engine

* Queue
* Worker Threads
* Order Scheduler

---

# Folder Structure

```text
Parallel Computing/
│
├── app.py
├── engine.py
├── database.py
├── orders.db
│
├── templates/
│   ├── admin.html
│   └── customer.html
│
├── static/
│   ├── app.js
│   ├── customer.js
│   └── style.css
│
└── developer.md
```

---

# Technologies Used

Backend

* Python 3.x
* Flask
* SQLite3
* Threading
* Queue

Frontend

* HTML5
* Tailwind CSS
* JavaScript

---

# Installation Guide

## Step 1: Install Python

Download and install Python:

https://www.python.org/downloads/

Verify installation:

```bash
python --version
```

---

## Step 2: Install Flask

Open terminal:

```bash
pip install flask
```

Verify installation:

```bash
pip show flask
```

---

# Running the System

## Step 1: Open Project Folder

```bash
cd "E:\Code\Parallel Computing"
```

---

## Step 2: Start Application

```bash
python app.py
```

Expected output:

```text
* Running on http://127.0.0.1:5000
```

---

## Step 3: Open Browser

Admin Dashboard

```text
http://127.0.0.1:5000
```

Customer Portal

```text
http://127.0.0.1:5000/customer
```

---

# Customer Portal

Features:

* Create Orders
* View Order History
* Track Order Progress
* View Timeline Updates
* Real-Time Refresh

Workflow:

1. Enter Customer Name
2. Select Product
3. Select Quantity
4. Click Submit Order
5. Monitor Order Progress

---

# Admin Dashboard

Features:

* Monitor Orders
* View Worker Status
* Track Fulfillment Progress
* Generate Test Orders
* Clear Database
* Real-Time Dashboard Updates

---

# Parallel Processing Implementation

The system uses:

```python
threading.Thread()
```

and

```python
queue.Queue()
```

Three worker threads operate simultaneously:

```text
Worker-Alpha
Worker-Beta
Worker-Gamma
```

Each worker continuously consumes orders from the queue and processes them independently.

---

# Fulfillment Stages

Orders progress through the following stages:

1. Pending in Queue
2. Queueing
3. Validating Payment
4. Checking Inventory
5. Generating Shipping Label
6. Packaging Asset
7. Ready for Shipment
8. Completed

---

# Database

Database File:

```text
orders.db
```

Stores:

* Orders
* Status Updates
* Worker Assignments
* Tracking Numbers
* Timestamps

---

# Troubleshooting

## Flask Not Found

Install Flask:

```bash
pip install flask
```

---

## Database Missing

Delete existing database:

```text
orders.db
```

Restart application:

```bash
python app.py
```

Database will be recreated automatically.

---

## Port Already In Use

Change port in app.py:

```python
app.run(
    host="0.0.0.0",
    port=5001,
    debug=True
)
```

---

# Authors

Developed for:

Parallel Computing Project

Technologies:

* Python
* Flask
* SQLite
* HTML
* Tailwind CSS
* JavaScript

Purpose:

Simulation of a distributed order fulfillment system utilizing parallel worker threads and queue-based processing.
