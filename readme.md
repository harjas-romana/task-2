# 🖥️ CS Projects API

A RESTful API for managing Computer Science projects using **FastAPI** and **Google Cloud Firestore**.

## 👤 Developer Information

| Field | Value |
|-------|-------|
| **Name** | Harjas Partap Singh Romana |
| **Registration Number** | 22BSA10120 |
| **College** | VIT Bhopal University |
| **Task** | Task 2 - CS Projects API |

---

## 🚀 Setup Instructions

### Step 1: Prerequisites

- Python 3.8 or higher
- Google Cloud account with Firestore enabled
- pip (Python package manager)

### Step 2: Create Google Cloud Firestore

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Navigate to **Firestore Database**
4. Click **Create Database**
5. Select **Native Mode**
6. Choose a location and create

### Step 3: Generate Service Account Key

1. Go to **IAM & Admin** → **Service Accounts**
2. Click **Create Service Account**
3. Name: `firestore-api-access`
4. Role: **Cloud Datastore User** or **Firebase Admin**
5. Click **Create Key** → **JSON**
6. Download and save as `serviceAccountKey.json`

### Step 4: Clone/Setup Project

```bash
# Create project directory
mkdir cs-projects-api
cd cs-projects-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt