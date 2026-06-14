# Parallel Fulfillment System

**Real-Time E-Commerce Order Processing and Tracking System**

A Flask-based web application developed to demonstrate the practical application of **Parallel and Distributed Computing** concepts through a simulated e-commerce fulfillment environment.

The system allows customers to place and track orders while administrators monitor inventory, worker performance, fulfillment progress, and operational analytics in real time.

---

## Project Objectives

This project aims to demonstrate:

* Queue-based task scheduling
* Multithreaded order processing
* Worker workload distribution
* Real-time monitoring and tracking
* Inventory validation and management
* Operational analytics
* Performance benchmarking between sequential and parallel execution

---

## Features

### Customer Portal

* User registration and login
* Session-based authentication
* Product browsing with images
* Real-time inventory synchronization
* Dynamic quantity validation
* Order placement
* Order history
* Order status filtering
* Timeline viewer for fulfillment progress

---

### Administrator Dashboard

* Main tracking board
* Real-time order monitoring
* Worker status monitoring
* Inventory management
* Product management
* Analytics dashboard
* Worker utilization statistics
* Sequential vs Parallel benchmarking
* Restore Demo Data functionality

---

## Parallel Processing Architecture

Incoming orders are placed into a queue and processed concurrently by multiple worker threads.

```text
Customer Order
       ↓
 Pending Queue
       ↓
 ┌─────────────┐
 │ Worker Alpha│
 ├─────────────┤
 │ Worker Beta │
 ├─────────────┤
 │Worker Gamma │
 └─────────────┘
       ↓
 SQLite Database
       ↓
 Timeline Updates
```

---

## Fulfillment Workflow

```text
Customer Places Order
        ↓
Pending in Queue
        ↓
Worker Assigned
        ↓
Validating Payment
        ↓
Checking Inventory
        ↓
Generating Shipping Label
        ↓
Packaging Asset
        ↓
Ready for Shipment
        ↓
Completed
```

If inventory is insufficient:

```text
Checking Inventory
        ↓
Out of Stock
```

---

## Technology Stack

### Backend

* Python 3.x
* Flask
* SQLite3
* Threading
* Queue

### Frontend

* HTML5
* Tailwind CSS
* Vanilla JavaScript
* Chart.js

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd Parallel-Fulfillment-System
```

Install dependencies:

```bash
pip install flask
```

Run the application:

```bash
python app.py
```

---

## Accessing the Application

Default URLs:

```text
Login:
http://127.0.0.1:5000/login

Signup:
http://127.0.0.1:5000/signup

Admin Dashboard:
http://127.0.0.1:5000/admin

Customer Portal:
http://127.0.0.1:5000/customer
```

---

## Project Structure

```text
Parallel-Fulfillment-System/
│
├── app.py
├── engine.py
├── database.py
├── templates/
├── static/
├── orders.db
├── README.md
├── DEVELOPER.md
└── AGENTS.md
```

---

## Educational Significance

This project demonstrates how concepts in Parallel and Distributed Computing can be applied to solve real-world business problems related to e-commerce order fulfillment.

The implementation highlights the benefits of concurrent execution, workload distribution, and real-time monitoring in improving operational efficiency.

---

## Authors

Developed as a course project for **Parallel and Distributed Computing**.

**Author:** John Benedict Reyes

**Institution:** TIP MANILA

**Academic Year:** 2025–2026
