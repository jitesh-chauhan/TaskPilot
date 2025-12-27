---

# To-Do App API Documentation

**Version:** 0.1.0

**Status:** Active Draft

## Overview

Welcome to the To-Do App API. This backend handles user registration, authentication, and full CRUD operations for task management.

### Quick Notes

* **Base URL:** (Assumed local) `http://localhost:8003`
* **Timestamps:** All dates (`due_date`, `created_at`) are stored as **UNIX timestamps (strings)**.
* **Responses:** Most API responses return a structured JSON object. Errors generally follow a standard format with a `message`.

---

## 1. User Management

Before managing tasks, we need to handle user accounts.

### Register a User

Create a new user account.

* **Endpoint:** `POST /api/v1/users`
* **Content-Type:** `application/json`

**Request Body:**

```json
{
  "email": "jane@example.com",
  "password": "securepassword123",
  "username": "Jane Doe" // (Optional additional props allowed)
}

```

**Response (200 OK):**

```json
{}

```

### Login

Authenticate a user.

* **Endpoint:** `POST /api/v1/login`
* **Content-Type:** `application/json`

**Request Body:**

```json
{
  "email": "jane@example.com",
  "password": "securepassword123"
}

```

### Get User Details

Fetch specific user info.

* **Endpoint:** `GET /api/v1/users`
* **Query Params:**
* `email` (Required): The email of the user to look up.



**Example Request:**
`GET /api/v1/users?email=jane@example.com`

---

## 2. To-Do Operations

The core logic for managing the task list.

### Create a To-Do

Adds a new item to the list.

* **Endpoint:** `POST /api/v1/todos/create`
* **Content-Type:** `application/json`

**Request Body:**
You can send arbitrary properties, but the backend expects the standard To-Do structure:

```json
{
  "title": "Buy Groceries",
  "description": "Milk, Eggs, Bread",
  "priority": "High",          // String: Low, Medium, High
  "due_date": "1730000000", // UNIX timestamp as string
  "email": "name@email.com"
}

```

### Get Todos

Fetch all tasks associated with a specific user.

* **Endpoint:** `GET /api/v1/todos`
* **Query Params:**
* `email` (Required): The user's email address.



**Response (200 OK):**
Returns a `TodoResponse` object.

```json
{
  "status": "success",
  "message": "Todos fetched successfully",
  "data": [
    {
      "id": "todo_1",
      "title": "Buy Groceries",
      "completed": false,
      "priority": "Medium",
      "created_at": "1729999999",
      "updated_at": "1729999999",
      "is_deleted": false,
      "deleted_at": ""
    }
  ]
}

```

### Delete a To-Do

Permanently removes a task.

* **Endpoint:** `DELETE /api/v1/todos`
* **Query Params:**
* `todo_id` (Required): The unique ID of the todo item.



**Example Request:**
`DELETE /api/v1/todos?todo_id=todo_1`

---

## 3. Data Models

Here is the structure of the objects used in the API.

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

## 4. Frontend Page Routes

*Just for reference.* These endpoints render the HTML pages or handle form redirects. If you are building a decoupled frontend (like React or Flutter), stick to the API endpoints above.

* `GET /` - Home/Redirect
* `GET /home` - Dashboard
* `GET /login` & `POST /login` - Login Page logic
* `GET /register` & `POST /register` - Registration Page logic
* `GET /add-todo` & `POST /add-todo` - Task Creation Page
* `POST /delete-todo/{todo_id}` - Form action to delete a task
* `GET /logout` - Logs the user out