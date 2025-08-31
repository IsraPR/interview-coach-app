# Stage 1: Builder - Installs dependencies
FROM python:3.12-slim as builder

WORKDIR /app

# Install uv, the Python package manager
RUN pip install uv

# Copy only dependency files to leverage Docker's build cache
COPY pyproject.toml .

# First, compile pyproject.toml to a standard requirements.txt file.
# Then, install the dependencies from that requirements.txt file.
# This avoids bash-specific syntax and is more robust.
RUN uv pip compile --no-annotate pyproject.toml -o requirements.txt && \
    uv pip install --system --no-cache -r requirements.txt


# Stage 2: Runner - The final, lean production image
FROM python:3.12-slim
# Set the working directory to where our code lives.
WORKDIR /app/src

# Copy the installed virtual environment from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application source code into the current directory (.) which is /app/src
COPY ./src .

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# This will be overridden by docker-compose for local development,
# but it's a good default for production.
ENV DJANGO_SETTINGS_MODULE=core.settings.production

EXPOSE 8000

# Daphne as the production ASGI server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]