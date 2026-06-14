# AGENTS.md

# Parallel Fulfillment System

Real-Time E-Commerce Order Processing and Tracking System

This document provides guidelines for human developers and AI coding assistants contributing to this project.

---

## Project Purpose

The Parallel Fulfillment System is an educational project developed to demonstrate the practical application of Parallel and Distributed Computing concepts using a simulated e-commerce fulfillment environment.

The primary objectives of this project are:

* Queue-based task scheduling
* Multithreaded order processing
* Worker workload distribution
* Real-time monitoring
* Operational analytics
* Sequential vs Parallel benchmarking

This is NOT intended to become a full-scale commercial e-commerce platform.

---

# Core Design Principles

## Preserve Existing UI

The Admin Dashboard and Customer Portal are considered finalized.

DO NOT:

* Redesign the user interface.
* Change the dark sidebar and white content layout.
* Change branding.
* Change typography.
* Change spacing.
* Introduce a different design language.

Only implement minimal modifications.

---

# Modification Philosophy

Before making changes:

1. Analyze the current implementation.
2. Preserve existing functionality.
3. Apply the minimum amount of code necessary.
4. Avoid large refactors.
5. Avoid rewriting files from scratch.

Preferred response format:

* REMOVE
* REPLACE
* ADD

---

# Features That Must Be Preserved

## Authentication

Preserve:

* Login
* Signup
* Session-based authentication
* Customer sessions
* Administrator sessions
* Logout functionality

Do not alter authentication workflows unless explicitly requested.

---

## Customer Portal

Preserve:

* Product browsing
* Product images
* Product inventory synchronization
* Order placement
* Order history
* Timeline viewer
* Order filtering
* Toast notifications
* Dynamic quantity validation

Do not redesign customer.html.

---

## Administrator Dashboard

Preserve:

* Dashboard
* Inventory Management
* Analytics
* Worker Status
* Timeline Viewer
* Worker Metrics
* Restore Demo Data

Do not redesign admin.html.

---

# Parallel Computing Rules

The fulfillment engine represents the core objective of this project.

Do not modify worker behavior without explicit instruction.

Preserve:

```text
Queue
↓
Worker Alpha
Worker Beta
Worker Gamma
```

Do not reduce the worker count.

Do not convert processing into synchronous execution.

---

# Fulfillment Workflow

Preserve this workflow:

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

If stock is insufficient:

```text
Checking Inventory
↓
Out of Stock
```

---

# Inventory Rules

Inventory deduction must occur during:

```text
Checking Inventory
```

Do NOT deduct inventory during:

```text
Order Submission
```

This behavior intentionally simulates warehouse operations.

---

# Worker Metrics

Preserve automatic collection of:

* Orders processed
* Busy time
* Utilization percentages

Metrics should be gathered inside:

```text
engine.py
```

Do not introduce manual calculations outside the worker lifecycle.

---

# Benchmarking Rules

Sequential vs Parallel benchmarking exists to demonstrate educational objectives.

Preserve:

Sequential:

```text
1 Worker
Orders processed one at a time
```

Parallel:

```text
3 Workers
Queue-based processing
```

Benchmark functionality must remain separate from production workflows.

---

# Reset Database Rules

Restore Demo Data should:

Reset:

* Orders
* Timeline records
* Worker statistics
* Analytics data
* Inventory quantities

Preserve:

* Administrator accounts
* Customer accounts
* Product images
* Authentication records

Never delete user accounts.

---

# API Guidelines

When adding APIs:

* Return JSON responses.
* Preserve SPA behavior.
* Avoid introducing full-page reloads.
* Validate administrator permissions where appropriate.

Example:

Success:

```json
{
    "success": true
}
```

Failure:

```json
{
    "success": false,
    "message": "Unauthorized."
}
```

---

# Frontend Guidelines

Prefer:

* Tailwind CSS
* Existing utility classes
* Vanilla JavaScript

Avoid introducing:

* React
* Vue
* Angular
* jQuery
* Bootstrap

unless explicitly requested.

---

# Bug Fix Policy

When fixing bugs:

DO:

* Fix only the affected area.
* Explain the root cause.
* Preserve surrounding behavior.

DO NOT:

* Rewrite entire files.
* Rename functions unnecessarily.
* Introduce unrelated improvements.

---

# Testing Checklist

Before finalizing modifications, verify:

Customer Portal:

* Login
* Logout
* Place Order
* Product synchronization
* Quantity validation
* Timeline viewer

Administrator Dashboard:

* Dashboard metrics
* Inventory Management
* Worker Status
* Analytics
* Restore Demo Data

Parallel Processing:

* Queue processing
* Worker assignment
* Inventory deduction
* Worker metrics
* Benchmarking

---

# Educational Scope

This project prioritizes demonstrating Parallel and Distributed Computing concepts over implementing comprehensive e-commerce functionality.

Avoid adding features such as:

* Shopping cart
* Coupons
* Reviews
* Payment gateways
* Live chat
* Email verification
* Wishlist systems

unless specifically requested.

---

# Contributor Notes

Always prioritize:

1. Stability
2. Educational objectives
3. Minimal code changes
4. Preservation of approved UI
5. Preservation of existing functionality

When uncertain:

Choose the solution that minimizes risk and maintains the original project intent.
