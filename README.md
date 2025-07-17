# Introduction
This simple codebase is a Minimal Reproducible Environment (MRE) for debugging purposes. It shows a possible way to put a FastAPI ASGI webapp behind an Apache web server (which only supports WSGI apps, if properly configured) which acts as an internal reverse proxy, which in turn is behind an external Caddy proxy server.
This is a reduced representation of the deployment configuration for TRUSTEE EU project.

# Explanation
- **docker-compose.yml**: This docker-compose.yml defines a minimal reproducible environment to simulate a production-like setup. Two services are deployed:
  - Caddy (Reverse Proxy & TLS Termination):
    - Exposes ports 80 (HTTP) and 443 (HTTPS).
    - Serves as the entry point for all external requests,handling HTTPS termination.
    - Proxies traffic to the xampp-fastapi service.
    - Uses the provided Caddyfile for configuration.

  - xampp-fastapi (Apache + FastAPI): A custom Docker image with the following characteristics:
    - Apache (from XAMPP) for serving PHP applications and reverse proxying to Uvicorn.
    - Uvicorn running a FastAPI application (possibily both frontend and API).
    - Managed via supervisord to run both services in parallel.
    - Accessible directly for debugging via localhost:8080.
    - Joins the same Docker network for internal communication with Caddy.

  In TRUSTEE: Not required.

- **Caddyfile**:
  - *e*xample.local: Defines the domain that Caddy listens on. For local development, ensure example.local maps to 127.0.0.1 in your /etc/hosts file. \
  `sudo nano /etc/hosts` --> Must contain a row "127.0.0.1   example.local"
  - tls internal: Instructs Caddy to generate a self-signed TLS certificate via its internal CA. This enables HTTPS locally without requiring external certificate providers.
  - reverse_proxy xampp-fastapi:80: Proxies all HTTPS requests to the xampp-fastapi container's Apache server running on port 80.

  This setup allows local HTTPS access to example.local, securely forwarding requests to the internal application stack.

  In TRUSTEE: Already set up by Forth.

- **xampp-fastapi/Dockerfile**:

  Based on XAMPP, extended with:
    - Python 3 + pip
    - FastAPI + Uvicorn
    - Supervisor for process management

  Configures:
    - Apache to serve PHP and proxy requests to FastAPI
    - Supervisor to run both Apache and FastAPI together

  Apache Proxy Modules and vhosts are enabled to allow request routing.
  
  This Dockerfile creates a unified environment where PHP (via Apache) and FastAPI (via Uvicorn) coexist, making them accessible behind Apache’s reverse proxy.

  In TRUSTEE: Must be changed and tested to add supervisord, FastAPI app, etc..

- **xampp-fastapi/apache_proxy.conf**:
  - Explanation:
    - <VirtualHost *:80>: Configures Apache to listen on port 80 for incoming HTTP requests.

    - DocumentRoot "/opt/lampp/htdocs": Serves PHP applications and static files from this directory.

    - <Directory'> block: Grants access permissions and allows .htaccess overrides for files within the document root.

  - Reverse Proxy Settings

    - ProxyPreserveHost On: Keeps the original Host header when forwarding requests.

    - ProxyPass /fastapi/ http://127.0.0.1:8000/:
    Proxies any request starting with /fastapi/ to the FastAPI application running on Uvicorn at localhost:8000.

    - ProxyPassReverse: Ensures that redirects and responses from FastAPI are correctly rewritten when passed back to the client.

  - Logging:
    - ErrorLog: Logs errors related to this virtual host

    - CustomLog: Logs all incoming requests and responses in a standard combined format.
  
  In TRUSTEE: Must be added to allow Apache to work as a proxy.

- **xampp-fastapi/supervisord.conf**:
  This configuration allows Supervisor to manage multiple processes within the same Docker container — specifically Apache (XAMPP) and FastAPI (via Uvicorn).
  
  - Global Settings:
    - nodaemon=true: Keeps Supervisor running in the foreground so the container remains active.
  
  - Apache Program
    - command: Starts Apache using XAMPP’s control script, followed by tail -f /dev/null to keep the process from exiting immediately (since lampp start backgrounds Apache).
    - stdout_logfile / stderr_logfile: Logs Apache’s standard output and errors for monitoring.
    - autostart / autorestart: Ensures Apache starts automatically and restarts if it crashes.

  - FastAPI Program
    - command: Launches the FastAPI app using Uvicorn, bound to 127.0.0.1:8000.
    - directory: Sets the working directory to where the FastAPI app is located (/opt/fastapi_app).
    - stdout_logfile / stderr_logfile: Captures logs for FastAPI.
    - autostart / autorestart: Enables automatic starting and restarting of the FastAPI service.
  
  In TRUSTEE: Must be added to configure running of both Apache and Uvicorn in the same Docker environment.

- **xampp-fastapi/fastapi_app/main.py**
  - It is just a simple webapp 
  
  In TRUSTEE: It's the trustee LLM application.

# Prerequisites (mandatory)
- Docker

# Prerequisites (optional)
- Portainer

# Build and run locally
Run the following command: \
`sudo docker compose up --build --force-recreate` 

from your local device to build and run the Docker compose stack.

# Test
Once the stack is up and running, run the following command: \
`curl -k https://example.local/fastapi/` 

from your local device to test the flow of requests \
*caddy --> Apache --> Uvicorn* 

is properly handled.