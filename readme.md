# 🖥️ CS Projects API

A RESTful API for managing Computer Science projects built with **FastAPI** and **Google Cloud Firestore**.

---

## 👤 Developer Information

| Field | Details |
|-------|---------|
| **Name** | Harjas Partap Singh Romana |
| **Registration Number** | 22BSA10120 |
| **College** | VIT Bhopal University |
| **Task** | Task 2 - CS Projects API |

---

## 🌐 Live API

**Base URL:** https://task-2-h4wt.onrender.com

**Swagger Docs:** https://task-2-h4wt.onrender.com/docs

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Welcome message |
| `GET` | `/info` | Developer information |
| `GET` | `/projects` | List all projects |
| `POST` | `/projects` | Create a new project |
| `GET` | `/projects/{id}` | Get project by ID |
| `PUT` | `/projects/{id}` | Update project by ID |
| `DELETE` | `/projects/{id}` | Delete project by ID |

---

## 📝 Sample Requests

### 1. Get Developer Info
```bash
curl https://task-2-h4wt.onrender.com/info
```

**Response:**
```json
{
  "name": "Harjas Partap Singh Romana",
  "registration_number": "22BSA10120",
  "college": "VIT Bhopal University",
  "note": "This is task 2 - CS Projects API"
}
```

---

### 2. Get All Projects
```bash
curl https://task-2-h4wt.onrender.com/projects
```

**Response:**
```json
{
  "success": true,
  "message": "Projects retrieved successfully",
  "count": 2,
  "projects": [
    {
      "id": "abc123",
      "title": "ML Image Classifier",
      "description": "A machine learning project",
      "programming_language": "Python",
      "difficulty_level": "Advanced",
      "createdAt": "2024-01-15T10:30:00"
    }
  ]
}
```

---

### 3. Create New Project
```bash
curl -X POST https://task-2-h4wt.onrender.com/projects \
  -H "Content-Type: application/json" \
  -d '{
    "title": "REST API with FastAPI",
    "description": "Building a RESTful API using Python FastAPI framework",
    "programming_language": "Python",
    "difficulty_level": "Intermediate"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Project created successfully",
  "project": {
    "id": "xyz789",
    "title": "REST API with FastAPI",
    "description": "Building a RESTful API using Python FastAPI framework",
    "programming_language": "Python",
    "difficulty_level": "Intermediate",
    "createdAt": "2024-01-15T12:00:00"
  }
}
```

---

### 4. Get Project by ID
```bash
curl https://task-2-h4wt.onrender.com/projects/{project_id}
```

---

### 5. Update Project
```bash
curl -X PUT https://task-2-h4wt.onrender.com/projects/{project_id} \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "difficulty_level": "Expert"
  }'
```

---

### 6. Delete Project
```bash
curl -X DELETE https://task-2-h4wt.onrender.com/projects/{project_id}
```

---

## 📊 Project Schema

```json
{
  "id": "auto-generated",
  "title": "string (3-200 chars)",
  "description": "string (10-2000 chars)",
  "programming_language": "string",
  "difficulty_level": "Beginner | Intermediate | Advanced | Expert",
  "createdAt": "timestamp (auto-generated)"
}
```

---

## ✅ Valid Field Values

**Programming Languages:**
```
Python, JavaScript, Java, C++, C, C#, Go, Rust, 
TypeScript, Ruby, PHP, Swift, Kotlin, R, MATLAB, 
Scala, Perl, SQL, Other
```

**Difficulty Levels:**
```
Beginner, Intermediate, Advanced, Expert
```

---

## 🛠️ Tech Stack

- **Framework:** FastAPI (Python)
- **Database:** Google Cloud Firestore
- **Hosting:** Render
- **Validation:** Pydantic

---

## 🚀 Run Locally

```bash
# Clone repository
git clone https://github.com/harjas-romana/task-2.git
cd task-2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add Firebase credentials
# Place serviceAccountKey.json in project folder

# Run server
uvicorn main:app --reload

# Open http://localhost:8000/docs
```

---

## 📄 License

Created for educational purposes - VIT Bhopal University

---

**Author:** Harjas Partap Singh Romana | 22BSA10120 | VIT Bhopal University


## 📋 Quick Reference Card

| Action | URL |
|--------|-----|
| **API Home** | https://task-2-h4wt.onrender.com/ |
| **Swagger Docs** | https://task-2-h4wt.onrender.com/docs |
| **Developer Info** | https://task-2-h4wt.onrender.com/info |
| **All Projects** | https://task-2-h4wt.onrender.com/projects |

---
