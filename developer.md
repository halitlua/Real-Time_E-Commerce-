# DEVELOPER.md

## LogisticsPro

### Distributed Real-Time E-Commerce Order Fulfillment System

---

# Project Overview

LogisticsPro is a distributed order fulfillment simulation developed using Python, Flet, SQLite, multithreading, and concurrent programming concepts.

The system demonstrates:

* Producer-Consumer Pattern
* Thread Pool Architecture
* Concurrent Task Processing
* Shared Database Communication
* Real-Time Order Tracking
* Multi-Client Interaction

The project was designed for Advanced Operating Systems and Parallel Computing coursework.

---

# System Architecture

## Components

### 1. Customer Portal (`customer.py`)

Responsibilities:

* Submit new orders
* View personal order history
* Track fulfillment progress
* View order timeline

Technology:

* Flet Web UI
* SQLite Database

---

### 2. Admin Dashboard (`admin.py`)

Responsibilities:

* Monitor all orders
* View worker status
* Run stress tests
* Monitor fulfillment metrics
* Observe queue activity

Technology:

* Flet Web UI
* SQLite Database

---

### 3. Processing Engine (`engine.py`)

Responsibilities:

* Poll database for new orders
* Push orders into queue
* Manage worker thread pool
* Execute fulfillment pipeline

Technology:

* queue.Queue
* threading.Thread

---

### 4. Shared Storage (`database.py`)

Responsibilities:

* Persist order information
* Store fulfillment timeline
* Provide communication layer between applications

Technology:

* SQLite

---

# Concurrent Programming Model

## Producer

Customer Portal

Produces orders:

```text
Customer
    ↓
database.add_order()
    ↓
SQLite
```

---

## Queue

Thread-safe FIFO queue.

```text
SQLite
    ↓
Poller Thread
    ↓
queue.Queue()
```

---

## Consumer

Worker threads consume queued orders.

```text
Worker Alpha
Worker Beta
Worker Gamma
```

Each worker processes orders independently.

---

# Fulfillment Pipeline

Every order passes through:

1. Order Created
2. Validating Payment
3. Checking Inventory
4. Generating Shipping Label
5. Packaging Asset
6. Ready For Shipment
7. Completed

Each stage is recorded in the timeline table.

---

# Database Schema

## orders

| Column          | Type    |
| --------------- | ------- |
| id              | TEXT    |
| customer        | TEXT    |
| product         | TEXT    |
| qty             | INTEGER |
| status          | TEXT    |
| worker          | TEXT    |
| tracking_number | TEXT    |
| created_at      | TEXT    |

---

## timeline

| Column    | Type    |
| --------- | ------- |
| id        | INTEGER |
| order_id  | TEXT    |
| timestamp | TEXT    |
| stage     | TEXT    |

---

# Worker Pool

Three daemon workers operate simultaneously.

```text
Worker Alpha
Worker Beta
Worker Gamma
```

Workers remain idle until orders appear in the queue.

---

# Stress Testing

Admin dashboard supports:

* Generate 10 Orders
* Generate 50 Orders
* Generate 100 Orders

Used to demonstrate:

* Queue growth
* Concurrent execution
* Worker balancing
* Real-time status updates

---

# Running the System

## Start Admin Dashboard

```bash
python admin.py
```

Default:

```text
http://localhost:8550
```

---

## Start Customer Portal

```bash
python customer.py
```

Default:

```text
http://localhost:8551
```

---

# Key Concepts Demonstrated

## Advanced Operating Systems

* Concurrency
* Scheduling
* Shared Resources
* Synchronization
* Producer Consumer Pattern

## Parallel Computing

* Worker Thread Pool
* Parallel Task Execution
* Queue-Based Work Distribution

## Database Systems

* Shared Persistent Storage
* Real-Time State Synchronization

---

# Future Enhancements

* User Authentication
* Inventory Module
* Analytics Dashboard
* REST API Layer
* Docker Deployment
* Distributed Worker Nodes

---

# Authors

Developed as an academic project demonstrating concurrent and distributed system design using Python.
