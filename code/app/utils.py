import smtplib
from email.message import EmailMessage
import app.config as config
import string
import random
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis_url = "redis://redis:6379"
    redis = aioredis.from_url(redis_url)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield

def generate_id():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(8))

def send_verification_email(email_to: str, token: str):
    try:
        verification_link = f"http://127.0.0.1:8000/auth/verify?token={token}"

        email = EmailMessage()
        email['Subject'] = 'Verify your email'
        email['From'] = config.EMAIL_LOGIN
        email['To'] = email_to

        email.set_content(
            f'Click on the link below to verify your email:\n\n{verification_link}'
        )

        with smtplib.SMTP_SSL(config.EMAIL_SERVER, config.EMAIL_PORT) as server:
            server.login(config.EMAIL_LOGIN, config.EMAIL_PASSWORD)
            server.send_message(email)

    except Exception as e:
        print(f"Failed to send verification email to {email_to}. Error: {e}")
