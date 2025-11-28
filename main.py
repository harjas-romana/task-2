"""
CS Projects API - A RESTful API for managing Computer Science projects
Author: Harjas Partap Singh Romana
Registration: 22BSA10120
College: VIT Bhopal University
Task 2 - CS Projects API
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from google.cloud import firestore
from google.oauth2 import service_account
from datetime import datetime
from typing import Optional
import json
import os

# ============================================
# FastAPI App Initialization
# ============================================
app = FastAPI(
    title="CS Projects API",
    description="A RESTful API for managing Computer Science projects using Firestore",
    version="1.0.0",
    contact={
        "name": "Harjas Partap Singh Romana",
        "email": "harjas42@icloud.com"
    }
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Firestore Database Initialization
# ============================================
db = None
projects_collection = None


def initialize_firestore():
    """Initialize Firestore with service account credentials"""
    global db, projects_collection
    
    try:
        # Method 1: Try environment variable (for Render deployment)
        firebase_credentials = os.environ.get("FIREBASE_CREDENTIALS")
        
        if firebase_credentials:
            # Parse JSON from environment variable
            cred_dict = json.loads(firebase_credentials)
            credentials = service_account.Credentials.from_service_account_info(cred_dict)
            db = firestore.Client(credentials=credentials, project=cred_dict.get("project_id"))
            projects_collection = db.collection("projects")
            print("✅ Connected to Firestore using environment variable!")
            return True
        
        # Method 2: Try local file (for local development)
        elif os.path.exists("serviceAccountKey.json"):
            credentials = service_account.Credentials.from_service_account_file(
                "serviceAccountKey.json"
            )
            db = firestore.Client(credentials=credentials, project=credentials.project_id)
            projects_collection = db.collection("projects")
            print("✅ Connected to Firestore using local file!")
            return True
        
        else:
            print("❌ No Firebase credentials found!")
            print("Set FIREBASE_CREDENTIALS env variable or add serviceAccountKey.json")
            return False
            
    except Exception as e:
        print(f"❌ Failed to connect to Firestore: {e}")
        return False


# Initialize on startup
initialize_firestore()


# ============================================
# Valid Values
# ============================================
VALID_DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]
VALID_LANGUAGES = [
    "Python", "JavaScript", "Java", "C++", "C", "C#", 
    "Go", "Rust", "TypeScript", "Ruby", "PHP", "Swift",
    "Kotlin", "R", "MATLAB", "Scala", "Perl", "SQL", "Other"
]


# ============================================
# Pydantic Models
# ============================================
class ProjectCreate(BaseModel):
    """Schema for creating a new project"""
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    programming_language: str = Field(..., min_length=1, max_length=50)
    difficulty_level: str = Field(...)

    @field_validator('difficulty_level')
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        if v not in VALID_DIFFICULTY_LEVELS:
            raise ValueError(f'Must be one of: {VALID_DIFFICULTY_LEVELS}')
        return v
    
    @field_validator('programming_language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        if v not in VALID_LANGUAGES:
            raise ValueError(f'Must be one of: {VALID_LANGUAGES}')
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    programming_language: Optional[str] = Field(None, min_length=1, max_length=50)
    difficulty_level: Optional[str] = Field(None)

    @field_validator('difficulty_level')
    @classmethod
    def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_DIFFICULTY_LEVELS:
            raise ValueError(f'Must be one of: {VALID_DIFFICULTY_LEVELS}')
        return v
    
    @field_validator('programming_language')
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_LANGUAGES:
            raise ValueError(f'Must be one of: {VALID_LANGUAGES}')
        return v


class InfoResponse(BaseModel):
    """Schema for info endpoint response"""
    name: str
    registration_number: str
    college: str
    note: str


# ============================================
# Helper Functions
# ============================================
def check_db_connection():
    """Check if Firestore is connected"""
    if projects_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected. Check FIREBASE_CREDENTIALS."
        )


def format_project(doc) -> dict:
    """Format Firestore document to dictionary"""
    project = doc.to_dict()
    project["id"] = doc.id
    if "createdAt" in project and project["createdAt"]:
        project["createdAt"] = project["createdAt"].isoformat() if hasattr(
            project["createdAt"], 'isoformat') else str(project["createdAt"])
    return project


# ============================================
# API ENDPOINTS
# ============================================

# GET /info - Developer Information
@app.get("/info", response_model=InfoResponse, tags=["Info"])
def get_info():
    """Returns developer information"""
    return InfoResponse(
        name="Harjas Partap Singh Romana",
        registration_number="22BSA10120",
        college="VIT Bhopal University",
        note="This is task 2 - CS Projects API"
    )


# GET /projects - List All Projects
@app.get("/projects", tags=["Projects"])
def get_all_projects():
    """Fetch all projects from Firestore"""
    check_db_connection()
    try:
        docs = projects_collection.order_by(
            "createdAt", direction=firestore.Query.DESCENDING
        ).stream()
        projects = [format_project(doc) for doc in docs]
        return {
            "success": True,
            "message": "Projects retrieved successfully",
            "count": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# POST /projects - Create New Project
@app.post("/projects", status_code=status.HTTP_201_CREATED, tags=["Projects"])
def create_project(project: ProjectCreate):
    """Create a new CS project"""
    check_db_connection()
    try:
        project_data = project.model_dump()
        project_data["createdAt"] = datetime.utcnow()
        doc_ref = projects_collection.add(project_data)
        created_id = doc_ref[1].id
        
        response_data = project_data.copy()
        response_data["id"] = created_id
        response_data["createdAt"] = project_data["createdAt"].isoformat()
        
        return {
            "success": True,
            "message": "Project created successfully",
            "project": response_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# GET /projects/{id} - Get Project by ID
@app.get("/projects/{project_id}", tags=["Projects"])
def get_project_by_id(project_id: str):
    """Fetch a single project by ID"""
    check_db_connection()
    try:
        doc = projects_collection.document(project_id).get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        return {
            "success": True,
            "message": "Project retrieved successfully",
            "project": format_project(doc)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# PUT /projects/{id} - Update Project
@app.put("/projects/{project_id}", tags=["Projects"])
def update_project(project_id: str, project: ProjectUpdate):
    """Update an existing project"""
    check_db_connection()
    try:
        doc_ref = projects_collection.document(project_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        
        update_data = {k: v for k, v in project.model_dump().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields provided")
        
        doc_ref.update(update_data)
        updated_doc = doc_ref.get()
        
        return {
            "success": True,
            "message": "Project updated successfully",
            "project": format_project(updated_doc)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# DELETE /projects/{id} - Delete Project
@app.delete("/projects/{project_id}", tags=["Projects"])
def delete_project(project_id: str):
    """Delete a project by ID"""
    check_db_connection()
    try:
        doc_ref = projects_collection.document(project_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
        
        deleted_project = format_project(doc)
        doc_ref.delete()
        
        return {
            "success": True,
            "message": "Project deleted successfully",
            "deleted_project": deleted_project
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# Root Endpoint
@app.get("/", tags=["Root"])
def root():
    """API Root - Welcome message"""
    return {
        "message": "Welcome to CS Projects API",
        "version": "1.0.0",
        "author": "Harjas Partap Singh Romana",
        "registration": "22BSA10120",
        "college": "VIT Bhopal University",
        "documentation": "/docs",
        "endpoints": [
            "GET /info",
            "GET /projects",
            "POST /projects",
            "GET /projects/{id}",
            "PUT /projects/{id}",
            "DELETE /projects/{id}"
        ]
    }













# """
# CS Projects API - A RESTful API for managing Computer Science projects
# Author: Harjas Partap Singh Romana
# Registration: 22BSA10120
# College: VIT Bhopal University
# Task 2 - CS Projects API
# """

# from fastapi import FastAPI, HTTPException, status
# from pydantic import BaseModel, Field, field_validator
# from google.cloud import firestore
# from google.oauth2 import service_account
# from datetime import datetime
# from typing import Optional
# import os

# # ============================================
# # FastAPI App Initialization
# # ============================================
# app = FastAPI(
#     title="CS Projects API",
#     description="A RESTful API for managing Computer Science projects using Firestore",
#     version="1.0.0",
#     contact={
#         "name": "Harjas Partap Singh Romana",
#         "email": "harjas@vitbhopal.ac.in"
#     }
# )

# # ============================================
# # Firestore Database Initialization
# # ============================================

# # Path to your service account JSON file
# # Place serviceAccountKey.json in the same folder as main.py
# SERVICE_ACCOUNT_FILE = "serviceAccountKey.json"

# db = None
# projects_collection = None

# def initialize_firestore():
#     """Initialize Firestore with service account credentials"""
#     global db, projects_collection
    
#     try:
#         # Check if service account file exists
#         if not os.path.exists(SERVICE_ACCOUNT_FILE):
#             print(f"❌ Service account file '{SERVICE_ACCOUNT_FILE}' not found!")
#             print("📝 Please download it from Firebase Console and place it in the project folder.")
#             return False
        
#         # Load credentials from service account file
#         credentials = service_account.Credentials.from_service_account_file(
#             SERVICE_ACCOUNT_FILE
#         )
        
#         # Initialize Firestore client with credentials
#         db = firestore.Client(credentials=credentials, project=credentials.project_id)
#         projects_collection = db.collection("projects")
        
#         print("✅ Connected to Firestore successfully!")
#         print(f"📂 Project ID: {credentials.project_id}")
#         return True
        
#     except Exception as e:
#         print(f"❌ Failed to connect to Firestore: {e}")
#         return False

# # Initialize on startup
# initialize_firestore()


# # ============================================
# # Valid Values
# # ============================================
# VALID_DIFFICULTY_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"]
# VALID_LANGUAGES = [
#     "Python", "JavaScript", "Java", "C++", "C", "C#", 
#     "Go", "Rust", "TypeScript", "Ruby", "PHP", "Swift",
#     "Kotlin", "R", "MATLAB", "Scala", "Perl", "SQL", "Other"
# ]


# # ============================================
# # Pydantic Models (Updated for Pydantic V2)
# # ============================================

# class ProjectCreate(BaseModel):
#     """Schema for creating a new project"""
#     title: str = Field(
#         ..., 
#         min_length=3, 
#         max_length=200,
#         description="Title of the CS project",
#         examples=["Machine Learning Image Classifier"]
#     )
#     description: str = Field(
#         ..., 
#         min_length=10, 
#         max_length=2000,
#         description="Detailed description of the project",
#         examples=["A deep learning project that classifies images using CNN"]
#     )
#     programming_language: str = Field(
#         ..., 
#         min_length=1, 
#         max_length=50,
#         description="Primary programming language used",
#         examples=["Python"]
#     )
#     difficulty_level: str = Field(
#         ...,
#         description="Difficulty level of the project",
#         examples=["Intermediate"]
#     )

#     @field_validator('difficulty_level')
#     @classmethod
#     def validate_difficulty(cls, v: str) -> str:
#         if v not in VALID_DIFFICULTY_LEVELS:
#             raise ValueError(f'difficulty_level must be one of: {VALID_DIFFICULTY_LEVELS}')
#         return v
    
#     @field_validator('programming_language')
#     @classmethod
#     def validate_language(cls, v: str) -> str:
#         if v not in VALID_LANGUAGES:
#             raise ValueError(f'programming_language must be one of: {VALID_LANGUAGES}')
#         return v


# class ProjectUpdate(BaseModel):
#     """Schema for updating an existing project (all fields optional)"""
#     title: Optional[str] = Field(
#         None, 
#         min_length=3, 
#         max_length=200,
#         examples=["Updated Project Title"]
#     )
#     description: Optional[str] = Field(
#         None, 
#         min_length=10, 
#         max_length=2000,
#         examples=["Updated project description"]
#     )
#     programming_language: Optional[str] = Field(
#         None, 
#         min_length=1, 
#         max_length=50,
#         examples=["JavaScript"]
#     )
#     difficulty_level: Optional[str] = Field(
#         None,
#         examples=["Advanced"]
#     )

#     @field_validator('difficulty_level')
#     @classmethod
#     def validate_difficulty(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None and v not in VALID_DIFFICULTY_LEVELS:
#             raise ValueError(f'difficulty_level must be one of: {VALID_DIFFICULTY_LEVELS}')
#         return v
    
#     @field_validator('programming_language')
#     @classmethod
#     def validate_language(cls, v: Optional[str]) -> Optional[str]:
#         if v is not None and v not in VALID_LANGUAGES:
#             raise ValueError(f'programming_language must be one of: {VALID_LANGUAGES}')
#         return v


# class InfoResponse(BaseModel):
#     """Schema for info endpoint response"""
#     name: str
#     registration_number: str
#     college: str
#     note: str


# # ============================================
# # Helper Functions
# # ============================================

# def check_db_connection():
#     """Check if Firestore is connected"""
#     if projects_collection is None:
#         raise HTTPException(
#             status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
#             detail="Database connection not available. Please check Firestore configuration and serviceAccountKey.json file."
#         )


# def format_project(doc) -> dict:
#     """Format Firestore document to dictionary"""
#     project = doc.to_dict()
#     project["id"] = doc.id
    
#     # Convert Firestore timestamp to string
#     if "createdAt" in project and project["createdAt"]:
#         if hasattr(project["createdAt"], 'isoformat'):
#             project["createdAt"] = project["createdAt"].isoformat()
#         elif hasattr(project["createdAt"], 'timestamp'):
#             # Firestore DatetimeWithNanoseconds
#             project["createdAt"] = project["createdAt"].isoformat()
#         else:
#             project["createdAt"] = str(project["createdAt"])
    
#     return project


# # ============================================
# # API ENDPOINTS
# # ============================================

# # ------------------------------
# # Endpoint 1: GET /info
# # ------------------------------
# @app.get(
#     "/info",
#     response_model=InfoResponse,
#     tags=["Info"],
#     summary="Get Developer Information"
# )
# def get_info():
#     """Returns information about the developer"""
#     return InfoResponse(
#         name="Harjas Partap Singh Romana",
#         registration_number="22BSA10120",
#         college="VIT Bhopal University",
#         note="This is task 2 - CS Projects API"
#     )


# # ------------------------------
# # Endpoint 2: GET /projects
# # ------------------------------
# @app.get(
#     "/projects",
#     tags=["Projects"],
#     summary="List All Projects"
# )
# def get_all_projects():
#     """Fetch all projects from Firestore"""
#     check_db_connection()
    
#     try:
#         docs = projects_collection.order_by(
#             "createdAt", 
#             direction=firestore.Query.DESCENDING
#         ).stream()
        
#         projects = [format_project(doc) for doc in docs]
        
#         return {
#             "success": True,
#             "message": "Projects retrieved successfully",
#             "count": len(projects),
#             "projects": projects
#         }
    
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching projects: {str(e)}"
#         )


# # ------------------------------
# # Endpoint 3: POST /projects
# # ------------------------------
# @app.post(
#     "/projects",
#     status_code=status.HTTP_201_CREATED,
#     tags=["Projects"],
#     summary="Create New Project"
# )
# def create_project(project: ProjectCreate):
#     """Create a new CS project"""
#     check_db_connection()
    
#     try:
#         project_data = project.model_dump()
#         project_data["createdAt"] = datetime.utcnow()
        
#         doc_ref = projects_collection.add(project_data)
#         created_id = doc_ref[1].id
        
#         response_data = project_data.copy()
#         response_data["id"] = created_id
#         response_data["createdAt"] = project_data["createdAt"].isoformat()
        
#         return {
#             "success": True,
#             "message": "Project created successfully",
#             "project": response_data
#         }
    
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error creating project: {str(e)}"
#         )


# # ------------------------------
# # Endpoint 4: GET /projects/{id}
# # ------------------------------
# @app.get(
#     "/projects/{project_id}",
#     tags=["Projects"],
#     summary="Get Project by ID"
# )
# def get_project_by_id(project_id: str):
#     """Fetch a single project by ID"""
#     check_db_connection()
    
#     try:
#         doc_ref = projects_collection.document(project_id)
#         doc = doc_ref.get()
        
#         if not doc.exists:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Project with ID '{project_id}' not found"
#             )
        
#         return {
#             "success": True,
#             "message": "Project retrieved successfully",
#             "project": format_project(doc)
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching project: {str(e)}"
#         )


# # ------------------------------
# # Endpoint 5: PUT /projects/{id}
# # ------------------------------
# @app.put(
#     "/projects/{project_id}",
#     tags=["Projects"],
#     summary="Update Project"
# )
# def update_project(project_id: str, project: ProjectUpdate):
#     """Update an existing project"""
#     check_db_connection()
    
#     try:
#         doc_ref = projects_collection.document(project_id)
#         doc = doc_ref.get()
        
#         if not doc.exists:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Project with ID '{project_id}' not found"
#             )
        
#         # Filter out None values (Pydantic V2)
#         update_data = {k: v for k, v in project.model_dump().items() if v is not None}
        
#         if not update_data:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="No valid fields provided for update"
#             )
        
#         doc_ref.update(update_data)
#         updated_doc = doc_ref.get()
        
#         return {
#             "success": True,
#             "message": "Project updated successfully",
#             "project": format_project(updated_doc)
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error updating project: {str(e)}"
#         )


# # ------------------------------
# # Endpoint 6: DELETE /projects/{id}
# # ------------------------------
# @app.delete(
#     "/projects/{project_id}",
#     tags=["Projects"],
#     summary="Delete Project"
# )
# def delete_project(project_id: str):
#     """Delete a project by ID"""
#     check_db_connection()
    
#     try:
#         doc_ref = projects_collection.document(project_id)
#         doc = doc_ref.get()
        
#         if not doc.exists:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"Project with ID '{project_id}' not found"
#             )
        
#         deleted_project = format_project(doc)
#         doc_ref.delete()
        
#         return {
#             "success": True,
#             "message": "Project deleted successfully",
#             "deleted_project": deleted_project
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error deleting project: {str(e)}"
#         )


# # ------------------------------
# # Root Endpoint
# # ------------------------------
# @app.get("/", tags=["Root"])
# def root():
#     """API Root - Welcome message"""
#     return {
#         "message": "Welcome to CS Projects API",
#         "version": "1.0.0",
#         "author": "Harjas Partap Singh Romana",
#         "documentation": "/docs",
#         "endpoints": {
#             "info": "GET /info",
#             "list_projects": "GET /projects",
#             "create_project": "POST /projects",
#             "get_project": "GET /projects/{id}",
#             "update_project": "PUT /projects/{id}",
#             "delete_project": "DELETE /projects/{id}"
#         }
#     }


# # ============================================
# # Run the application
# # ============================================
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)