# Introduction
This simple codebase is a Minimal Reproducible Environment (MRE) for debugging purposes. It shows a possible way to put a FastAPI ASGI webapp behind an Apache web server (which only supports WSGI apps, if properly configured) which acts as an internal reverse proxy, which in turn is behind an external Caddy proxy server.
This is a reduced representation of the deployment configuration for TRUSTEE EU project.

# Explanation
- **docker-compose.yml**: This docker-compose.yml defines a minimal reproducible environment to simulate a production-like setup. Two services are deployed:
  - Caddy (Reverse Proxy & TLS Termination):
    - Exposes ports 80 (HTTP) and 443 (HTTPS).
    - Serves as the entry point for all external requests, handling HTTPS termination.
    - Proxies traffic to the xampp-fastapi service.
    - Uses the provided Caddyfile for configuration.

  - xampp-fastapi (Apache + FastAPI): A custom Docker image with the following characteristics:
    - Apache (from XAMPP) for serving PHP applications and reverse proxying to Uvicorn.
    - Uvicorn running a FastAPI application (possibily both frontend and API).
    - Managed via supervisord to run both services in parallel.
    - Maps internal port 80 (Apache) to external 3600 for debugging purposes.
    - Joins the same Docker network for internal communication with Caddy, with static internal IPs.

  In TRUSTEE: Not strictly required.

- **Caddyfile**:
  - tai-sdf.trustee-1.ics.forth.gr: Defines the domain that Caddy listens on. For local development, ensure tai-sdf.trustee-1.ics.forth.gr maps to 127.0.0.1 in your /etc/hosts file. \
  `sudo nano /etc/hosts` --> Must contain a row "127.0.0.1   tai-sdf.trustee-1.ics.forth.gr". \
  /etc/hosts represents a local, static DNS lookup. It allows the OS to resolve a hostname to an IP address without querying DNS servers. It's checked before any DNS lookup, providing a quick and manual way to define name-to-IP mappings. This is how, for instance, localhost is resolved to 127.0.0.1.
  - tls internal: Instructs Caddy to generate a self-signed TLS certificate via its internal CA. This enables HTTPS locally without requiring external certificate providers. Browsers do not trust self-signed certificates by default — leading to warnings like "You are not securely connected" or "Your connection is not private".
  - reverse_proxy xampp-fastapi:80: Proxies all HTTPS requests to the xampp-fastapi container's Apache server (running on port 80).

  This setup allows local HTTPS access to tai-sdf.trustee-1.ics.forth.gr, securely forwarding requests to the internal application stack.

  In TRUSTEE: Already set up by Forth.

- **xampp-fastapi/Dockerfile**:

  Based on a XAMPP base image which has been extended with the following, in order to handle 2 web servers into a single Docker environment:
    - Python 3.12 + pip
    - FastAPI + Uvicorn
    - Supervisor (for process management)

  During the build process:
    - Runtime environment variables are declared as VENV RUNTIME_VAR=$BUILD_TIME_VAR (to allow overrinding them at build time).
    - Python3.12 is compiled from source and installed (without replacing system-wide Python installation)
    - pip package manager is installed and used to both install supervisor process manager and FastAPI webapp dependencies
    - Python FastAPI app source code is deployed to the Docker container
    - Apache is configured to serve PHP and to proxy requests to FastAPI
    - supervisord is configured to run both Apache and FastAPI concurrently
    - supervisord is called as entry point for the Docker

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

    - ProxyPass /ui_llm http://172.44.0.21:8000/ui_llm:
    Proxies any request starting with /ui_llm/ to the FastAPI application running on Uvicorn at 172.44.0.21:8000.

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
    - command: Launches main.py, which defines the whole FastAPI app and hosts it via Uvicorn
    - directory: Sets the working directory to where the FastAPI app is located (/opt/fastapi_app).
    - stdout_logfile / stderr_logfile: Captures logs for FastAPI.
    - autostart / autorestart: Enables automatic starting and restarting of the FastAPI service.
  
  In TRUSTEE: Must be added to configure running of both Apache and Uvicorn in the same Docker environment.

- **xampp-fastapi/Trustee_LLM**
  - Our FastAPI web app. 
  
  In TRUSTEE: It's the Trustee LLM application.

# Prerequisites (mandatory)
- Docker
- XAMPP suite (v7.4.7)

# Prerequisites (optional)
- Portainer

# Build and run locally
Run the following command: \
`sudo docker compose up --build --force-recreate` 

from your local device to build and run the Docker compose stack.

# Test
Once the stack is up and running, go to your web browser and make a request to: \
`https://tai-sdf.trustee-1.ics.forth.gr/ui_llm/` 

from your local device to test the flow of requests \
*caddy --> Apache --> Uvicorn* 

is properly handled.

# Save a .tar containing the Docker image
You'll need the image reference (from "Images" --> Tags in Portainer, or REPOSITORY in `sudo docker images`)
`sudo docker save -o xampp-fastapi.tar apache_fastapi-xampp-fastapi`