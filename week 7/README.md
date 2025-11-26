# Week 7 — Secure Authentication System

**Name:** Madhu Haldurai Ranjith 
**ID:** M01090955 
**Programme:** BSc Information Technology  

---

## Overview

This project is a terminal-based authentication module designed to simulate a simple but realistic login system. It focuses on secure password handling, user account management, session tracking, and input validation. All data is handled using simple text files for clarity and portability.

---

## What the System Does

- Stores passwords securely with **bcrypt hashing**
- Registers users with selectable roles (user, admin, analyst)
- Avoids duplicate usernames during registration
- Logs in users via hashed password verification
- Provides a password strength rating (Weak / Medium / Strong)
- Validates both username and password formats
- Implements a 5-minute lockout after 3 failed login attempts
- Creates unique session tokens for logged-in users
- Persists data using text files for users, sessions, and failed attempts

---

## Core Features

### 🔐 Password Security
- Hashing powered by **bcrypt**
- Automatic salting for every password
- No plaintext password storage

### 👥 User Management
- Registration with validation checks
- Duplicate usernames are blocked
- Role assignment included

### 🚪 Login System
- Secure bcrypt-based password comparisons
- Failed login tracking
- Temporary lockout after repeated errors

### 🧪 Input Validation
**Username requirements:**
- 3–20 characters  
- Alphanumeric + underscores only  
- No spaces  

**Password requirements:**
- 6–50 characters  
- Must include:
  - Uppercase letter  
  - Lowercase letter  
  - Number  
  - Special character  

### 🧵 Session Handling
- Generates secure random tokens using `secrets`
- Logs timestamped sessions
- Stored in `sessions.txt`

---

## File Structure

| File | Purpose |
|------|---------|
| `users.txt` | Stores `username,hashed_password,role` |
| `sessions.txt` | Stores session token + timestamp |
| `failed_attempts.txt` | Tracks incorrect login attempts |

---

## Technologies Used

- **bcrypt** for hashing  
- **secrets** for token generation  
- **re** for validation  
- **time** for timestamps and lockout logic  
- **os** for file handling
