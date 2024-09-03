# Accuknox Social Media Application Backend

This repository contains the backend code for a social media application. It provides a REST API for user management, friend requests, and user search functionalities, along with rate-limiting mechanisms to control API usage. This guide will help you set up the application using Docker, manage the dependencies, and run the application locally.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Getting Started](#getting-started)
- [Running Migrations](#running-migrations)
- [Testing the APIs](#testing-the-apis)
- [Rate Limiting](#rate-limiting)

## Prerequisites

Before you begin, make sure you have the following installed:

1. **Docker**: The application uses Docker to manage dependencies and run the application in isolated containers. [Install Docker](https://docs.docker.com/engine/install/).

2. **Docker Compose**: Used for managing multi-container Docker applications. It comes with Docker Desktop by default.

3. **Git**: For cloning the repository. [Install Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).

## Installation

To set up the application on your local machine, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/accuknox-social-media-backend.git
   cd accuknox-social-media-backend
   ```

2. **Create a Virtual Environment (Optional but Recommended)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   If you're not using Docker, install the dependencies manually using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Variables

For this backend application, the default Django settings are used without the need for additional environment variables since it runs on SQLite (the default Django database). However, if you plan to switch to another database (like PostgreSQL), you need to set up the following environment variables in a `.env` file:

- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`
- `DATABASE_HOST`
- `DATABASE_PORT`

## Getting Started

To get the server up and running, follow these steps:

1. **Build and Start the Docker Containers**:
   Ensure you are in the project root directory where the `docker-compose.yml` file is located and run:
   ```bash
   docker-compose up --build
   ```

   This will build the Docker image, set up the required containers, and start the Django server at `http://localhost:8000`.

2. **Access the Application**:
   The application will be accessible at `http://localhost:8000`.

## Running Migrations

Once the Docker containers are up and running, you need to run the database migrations:

1. **Run Migrations**:
   ```bash
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

2. **Create a Superuser (for Django Admin Access)**:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## Testing the APIs

To test the APIs, you can use tools like **Postman** or **cURL**. Import the provided Postman collection (if available) into Postman to test the endpoints with pre-configured requests, example payloads, and expected responses.

### API Endpoints Overview

1. **User Management**: Create users, login, etc.
2. **Friend Requests**: Send and manage friend requests between users.
3. **Search Users**: Search for users by name or email.

Refer to the `urls.py` file for the list of all available endpoints.

## Rate Limiting

The application enforces a rate limit of 3 friend requests per minute per user to prevent spamming. If a user exceeds this limit, they will receive an HTTP 429 (Too Many Requests) error.
