# Pastebin Clone Backend

## Overview

This project is a backend for a Pastebin clone. It provides an API for user management, post management, and authentication. The project uses JWT tokens for authentication and incorporates caching using FastAPI Cache and Redis to enhance performance.

## Features

- **JWT Authentication**:
  - User registration
  - Login with access token and refresh token
  - Email verification using tokens
  - Access token refresh using refresh token

- **Post Management**:
  - Create new posts
  - Retrieve list of posts
  - Retrieve a post by ID

- **Caching**:
  - Uses Redis for caching requests via FastAPI Cache

## Installation and Setup

### Prerequisites

- Python 3.7+
- Redis server

### Installation

1. Install dependencies:

Ensure you have Python and pip installed. Then, install the required packages:
```sh
pip install -r requirements.txt
```

2. Set up Redis:

Make sure Redis is installed and running on your machine.

3. Start the FastAPI server:

```sh
cd code
python main.py
```


### Configuration
# code/app/config.py
```python
SECRET_KEY = "oyYIOx2QDGpA+1b5ebINLjW7szSQUleSnC+oPaOrFL8=" #openssl rand -base64 32
ALGORITHM = "HS256"
EMAIL_SERVER = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_LOGIN = "your_email@gmail.com"
EMAIL_PASSWORD = "your_email_password"
```

Replace the placeholder values with your actual configuration details.