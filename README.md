# AI Job Interview Coach

This project is Restful API that leverages AI to help users practice and improve their interview skills. It provides real-time feedback and interactive sessions powered by AWS Bedrock and the Nova Sonic speech-to-speech model.

The backend is built with Python 3.12, Django, and Django Ninja, and is designed to be a scalable, production-ready, and containerized application.

## Core Features

*   **User Authentication:** Secure JWT-based authentication for users.
*   **Job Profiles:** Users can create and manage profiles for specific job roles they want to practice for, including resume and job description details.
*   **Interactive AI Sessions:** Real-time, voice-based interview practice sessions using AWS Nova Sonic.
*   **Session Feedback:** AI-driven feedback and ratings for completed interview sessions.
*   **Scalable Architecture:** Built with a clean `src` layout, service layers, and a modular app structure.

## Tech Stack

*   **Backend:** Python 3.12, Django 5.1, Django Ninja
*   **Real-time:** Django Channels (WebSockets)
*   **Database:** PostgreSQL
*   **AI Services:** AWS Bedrock (Nova Sonic), Strands Agents
*   **Async Tasks:** Celery with Redis
*   **Development Environment:** Docker, Docker Compose
*   **Package Management:** `uv`
*   **Task Runner:** `poe-the-poet`

---

## Getting Started

### Prerequisites

*   **Docker** and **Docker Compose**: Ensure they are installed and the Docker daemon is running. [Install Docker](https://docs.docker.com/get-docker/)
*   **Python 3.12+**: Required for running local setup scripts.
*   **`uv`**: The project's package manager. Install it with `pip install uv`.

### 1. Clone the Repository

```bash
git clone https://github.com/IsraPR/interview-coach-app.git
cd interview-coach-app
```

### 2. Set Up the Environment

This project uses `poe-the-poet` as a task runner, which is defined in `pyproject.toml`. First, set up a local virtual environment and install the development dependencies.

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install the project in editable mode with development dependencies
uv pip install -e .[dev]
```

### 3. Configure Environment Variables

The application is configured using environment variables. You will need to create a `.env` file for the full stack and a `.env.lite` file for a minimal setup.

**For a minimal setup (API + DB only):**
1.  Copy the example lite environment file:
    ```bash
    cp .env.lite.example .env.lite
    ```
2.  Open `.env.lite` and fill in the required values, especially your AWS credentials.

**For the full stack (API, DB, Celery, Redis):**
1.  Copy the main example environment file:
    ```bash
    cp .env.example .env
    ```
2.  Open `.env` and fill in all required values.

### 4. Running the Application with Docker

You have two primary ways to run the application locally.

#### Option A: Lite Mode (Recommended for most API development)

This mode starts only the Django API and the PostgreSQL database, which is faster and uses fewer resources.

```bash
poe up-lite
```

The API will be available at `http://localhost:8000/api/`. Hot-reloading is enabled, so changes to the code in the `src/` directory will automatically restart the server.

#### Option B: Full Stack Mode

This mode starts all services: the API, database, Celery worker, and Redis. This is necessary if you are working on features that involve background tasks or the WebSocket channel layer.

```bash
poe up-full
```

### 5. Database Migrations

The database tables need to be created. The first time you run the application, or after you make changes to any `models.py` file, you will need to create and apply migrations.

**Important:** Run these commands in a **separate terminal** while your application is running (`poe up-lite` or `poe up-full`).

1.  **Create new migration files:**
    ```bash
    # For a specific app (e.g., users)
    poe makemigrations users

    # To create a named migration for better history
    poe makemigrations users --name "add_bio_to_user_model"
    ```

2.  **Apply the migrations to the database:**
    ```bash
    poe migrate
    ```

### 6. Create a Superuser

To access the Django Admin dashboard, you need a superuser account.

```bash
# Run this in a separate terminal
docker compose exec api python manage.py createsuperuser
```

Follow the prompts to create your admin user. You can then access the admin dashboard at `http://localhost:8000/admin/`.

### 7. Stopping the Application

To stop all running Docker containers and remove the network, run:

```bash
poe down
```

---

## API Documentation

Postman: https://documenter.getpostman.com/view/19026408/2sB3QDuC9Q