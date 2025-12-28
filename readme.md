
**Version:** 0.1.0  
**Status:** Active Draft  

**Tech Stack:** FastAPI (Backend), Jinja2 (Tempplates), MongoDB (Database)

## 📌 Overview

The To-Do App API provides a backend service for user authentication and task management.
It allows users to create, update, retrieve, and delete to-do items in a secure and
scalable manner.

The API is built using FastAPI for high performance and MongoDB for flexible,
document-oriented data storage. It is suitable for both web and mobile clients.


### 2. Installation & Setup

```bash
# Create and Activate Virtual Environment
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows

# Install Dependencies
pip install -r requirements.txt

```

### 3. Environment Configuration

Create a `.env` file in the cofig directory:

```env
DB_NAME="todo_app"
DATABASE_URL="mongodb://localhost:27017"
JWT_SECRET_KEY="change_me_later"

```

### 4. Running

```bash
python run.py
```

### The application will be available at:
    http://127.0.0.1:8003

## API Documentation

---

### FastAPI automatically generates interactive API documentation.

---
#### Swagger UI

    http://127.0.0.1:8003/docs


#### ReDoc

    http://127.0.0.1:8003/redoc

##  API Endpoints

### 1. User Management

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/users` | Register a new user |
| `POST` | `/api/v1/login` | Authenticate and get token |
| `GET` | `/api/v1/users` | Fetch user details (Query: `email`) |


### 2. To-Do Operations

| Method   | Endpoint                 | Description                        |
|----------|--------------------------|------------------------------------|
| `POST`   | `/api/v1/todos/create`   | Create a new task                  |
| `GET`    | `/api/v1/todos`          | List all tasks for a user          |
| `DELETE` | `/api/v1/todos`          | Remove a task (Query: `todo_id`)   |
| `PUT`    | `/api/v1/todos/complete` | Complete a task (Query: `todo_id`) |

### 3. Frontend Page Routes


* `GET /` - Home/Redirect
* `GET /home` - Dashboard
* `GET /login` & `POST /login` - Login Page logic
* `GET /register` & `POST /register` - Registration Page logic
* `GET /add-todo` & `POST /add-todo` - Task Creation Page
* `POST /delete-todo/{todo_id}` - Form action to delete a task
* `PUT /complete-todo/{todo_id}` -Form action to complete a task
* `GET /logout` - Logs the user out

---

## 📊 Data Models

### Todo Item

| Field | Type    | Description           |
| --- |---------|-----------------------|
| `id` | String  | Unique Primary Key    |
| `title` | String  | Max 200 chars (Required) |
| `description` | String  | Max 1000 chars        |
| `priority` | String  | Low, Medium, High|    
| `completed` | Boolean | Default: `false`      |
| `due_date` | String  | UNIX timestamp (ms)   |
| `created_at` | String  | UNIX timestamp        |
| `is_deleted`| Boolean | Default: `false`      |
|`deleted_at`|String|UNIX timestamp |
---

### User Model

| Field        | Type    | Description             |
| ------------ | ------- | ----------------------- |
| `id`         | String  | Unique Primary Key      |
| `username`   | String  | Max 200 chars           |
| `email`      | String  | Valid email             |
| `password`   | String  | Hashed password         |
| `role`       | String  | User role               |
| `enabled`    | Boolean | Default `false`         |
| `created_at` | String  | UNIX timestamp **(ms)** |
| `updated_at` | String  | UNIX timestamp **(ms)** |

---
---

## 📂 Project Structure

```text
.
├── app
│   ├── apis            # API Logic & Pydantic Models (Auth, Todos, Users)
│   ├── database        # DB Connection
│   ├── routes          # Unified Router Logic
│   ├── templates       # HTML Templates
│   └── utils           # Auth & Logging Helpers
├── core                # Global Config & Settings
├── tests               # Pytest Suite
├── requirements.txt    # Production Dependencies
└── run.py              # Application Entry Point

```

---

## 🧪 Testing

The project uses `pytest` for automated testing.

```bash
# Run all tests
./run_tests.sh

```

---
