# Secura-Med : Dual Encryption Based Framework for Medical Images.
_A Python-Based System for Protecting Sensitive Healthcare Data._

---

## 📖 Overview
Secura-Med is a dual-layer encryption framework designed to secure medical images (CT, MRI, X-ray, etc.) during storage and transmission.
The system combines AES (symmetric encryption) for fast image encryption and RSA (asymmetric encryption) for secure key protection.

---

## ✨ Features
- Dual-Layer Security using AES + RSA
- Secure Key Generation, Encryption & Decryption
- Support for Medical DICOM Images (.dcm)
- User authentication & key management  
- Easy to extend for more cryptographic methods
---

## 📋 Prerequisites
- **Python 3.x** (>= 3.8)  
- Required modules (listed in `requirements.txt`)  

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/isha74/Cryptography--Dual_Security_System.git
   cd Cryptography--Dual_Security_System


2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source venv/bin/activate
   # For Windows: .venv\Scripts\activate

3. **Install requirements:**
    ```bash
   pip install -r requirements.txt
   python -m pip install --upgrade pip

## How to run the project:

**Start the Web Application**
   ```bash
   python src\web_app.py
```

**Initialize / Download the Database**
   ```bash
   python src\database.py 

