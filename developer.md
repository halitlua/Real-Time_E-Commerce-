# DEVELOPER.md

## Parallel Fulfillment System

**Real-Time E-Commerce Order Processing and Tracking System**

---

## Overview

The Parallel Fulfillment System is a Flask-based web application developed to demonstrate the practical application of Parallel and Distributed Computing concepts in a simulated e-commerce environment.

The system allows customers to place and track orders while administrators monitor fulfillment activities, worker performance, inventory levels, and operational analytics.

The application emphasizes queue management, multithreading, and real-time processing to illustrate how parallel execution improves efficiency in business operations.

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

### Database

* SQLite

---

## Project Structure

```
Parallel Computing/
│
├── app.py
├── engine.py
├── database.py
├── templates/
│   ├── login.html
│   ├── signup.html
│   ├── admin.html
│   └── customer.html
│
├── static/
│   ├── app.js
│   ├── customer.js
│   ├── uploads/
│   └── images/
│
├── orders.db
├── README.md
└── DEVELOPER.md
```

---

## Core Features

### Customer Portal

* User registration and login
* Session-based authentication
* Product browsing
* Product image previews
* Real-time inventory synchronization
* Order placement
* Order history
* Order timeline viewer
* Order status filtering

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

### Queue-Based Processing

Incoming orders are initially placed into a queue.

```
Customer Order
      ↓
 Pending Queue
      ↓
 Worker Assignment
```

Python's Queue module ensures fair scheduling and organized task distribution.

---

### Worker Threads

The fulfillment engine utilizes three concurrent worker threads:

* Worker Alpha
* Worker Beta
* Worker Gamma

Each worker independently processes queued orders.

```
Queue
├─ Worker Alpha
├─ Worker Beta
└─ Worker Gamma
```

---

## Fulfillment Workflow

Each order progresses through the following stages:

1. Validating Payment
2. Checking Inventory
3. Generating Shipping Label
4. Packaging Asset
5. Ready for Shipment
6. Completed

If inventory is insufficient:

```
Checking Inventory
        ↓
Out of Stock
```

The order terminates safely without affecting other worker threads.

---

## Inventory Workflow

Inventory deduction occurs during fulfillment processing rather than order submission.

Workflow:

```
Customer Places Order
        ↓
Pending in Queue
        ↓
Worker Assigned
        ↓
Checking Inventory
        ↓
Stock Deducted
        ↓
Fulfillment Continues
```

This approach better simulates real-world warehouse operations.

---

## Worker Metrics

The system records:

### Orders Processed

Example:

```
Worker Alpha : 42 Orders
Worker Beta  : 38 Orders
Worker Gamma : 40 Orders
```

### Busy Time

Example:

```
Worker Alpha : 8 Minutes
Worker Beta  : 7 Minutes
Worker Gamma : 9 Minutes
```

### Utilization

Example:

```
Alpha : 35%
Beta  : 32%
Gamma : 33%
```

Metrics are automatically collected during worker execution.

---

## Benchmarking

The application compares:

### Sequential Processing

* Single worker
* Orders processed one at a time

### Parallel Processing

* Three concurrent workers
* Queue-based distribution

Sample Benchmark:

| Orders | Sequential | Parallel |
| ------ | ---------- | -------- |
| 10     | 34 sec     | 12 sec   |
| 50     | 168 sec    | 58 sec   |
| 100    | 336 sec    | 113 sec  |

These measurements demonstrate the benefits of parallel execution.

---

## Database Reset

The administrator can restore the application to its demonstration state.

The reset operation:

### Resets

* Orders
* Timelines
* Worker statistics
* Analytics data
* Inventory quantities

### Preserves

* Administrator accounts
* Customer accounts
* Product images
* Authentication data

---

## Running the Application

Install dependencies:

```bash
pip install flask
```

Start the application:

```bash
python app.py
```

Access:

```
Login:
http://127.0.0.1:5000/login

Admin Dashboard:
http://127.0.0.1:5000/admin

Customer Portal:
http://127.0.0.1:5000/customer
```

---

## Educational Objectives

This project was developed to demonstrate:

* Queue management
* Multithreading
* Concurrent task execution
* Real-time monitoring
* Worker workload distribution
* Operational analytics
* Performance benchmarking
* Practical applications of Parallel and Distributed Computing concepts

---

## Authors

Developed as a course project for Parallel and Distributed Computing.

Author:
John Benedict Reyes

Institution:
TIP MANILA

Academic Year:
2025–2026
