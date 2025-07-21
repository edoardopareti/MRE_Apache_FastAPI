FROM tomsik68/xampp:latest

# Copy PHP web application code and artifacts into /opt/lampp for serving
# COPY /opt/lampp /opt/lampp

# Setup build-time variables (FastAPI app)
ARG APP_BACKEND_PORT=8000
ARG APP_DESCRIPTION=Introduction of an LLM backend for TAI-SDF RINA AI trustworthiness assessment
ARG APP_TITLE=TAI-SDF LLM - Questions Report
ARG AZURE_OPENAI_API_KEY= 
ARG AZURE_OPENAI_ENDPOINT= 
ARG ENVIRONMENT=test
ARG OPENAI_API_KEY=overwrite_me!
ARG REQUISITES_DB_HOST=127.0.0.1
ARG REQUISITES_DB_NAME=tai-sdf
ARG REQUISITES_DB_PASSWORD= 
ARG REQUISITES_DB_PORT=3326
ARG REQUISITES_DB_USER=root
ARG REQUISITES_JSON_API_KEY=overwrite_me_too!
ARG REQUISITES_JSON_HOST=tai-sdf.trustee-1.ics.forth.gr
ARG REQUISITES_JSON_PORT=3600
ARG REQUISITES_JSON_PROTOCOL=http
ARG REQUISITES_JSON_QUESTIONS_PATH=Trustee/php/externalApiGetQuestions.php
ARG SSL_CERT_PATH=ssl/server.crt
ARG SSL_KEY_PATH=ssl/server.key

# Setup runtime environment variable (FastAPI app), copying the value from the build-time ARG into the runtime ENV.
ENV APP_BACKEND_PORT=${APP_BACKEND_PORT}
ENV APP_DESCRIPTION=${APP_DESCRIPTION}
ENV APP_TITLE=${APP_TITLE}
ENV AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}
ENV AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}
ENV ENVIRONMENT=${ENVIRONMENT}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV REQUISITES_DB_HOST=${REQUISITES_DB_HOST}
ENV REQUISITES_DB_NAME=${REQUISITES_DB_NAME}
ENV REQUISITES_DB_PASSWORD=${REQUISITES_DB_PASSWORD}
ENV REQUISITES_DB_PORT=${REQUISITES_DB_PORT}
ENV REQUISITES_DB_USER=${REQUISITES_DB_USER}
ENV REQUISITES_JSON_API_KEY=${REQUISITES_JSON_API_KEY}
ENV REQUISITES_JSON_HOST=${REQUISITES_JSON_HOST}
ENV REQUISITES_JSON_PORT=${REQUISITES_JSON_PORT}
ENV REQUISITES_JSON_PROTOCOL=${REQUISITES_JSON_PROTOCOL}
ENV REQUISITES_JSON_QUESTIONS_PATH=${REQUISITES_JSON_QUESTIONS_PATH}
ENV SSL_CERT_PATH=${SSL_CERT_PATH}
ENV SSL_KEY_PATH=${SSL_KEY_PATH}

# Update package lists and install required build dependencies for Python.
# Then, download the Python 3.12 source code from the official Python website,
# and compile it from source using all available CPU cores (via nproc).
# Finally, install the compiled Python binary without overwriting the system Python.
RUN apt-get update && \
    apt-get install -y wget build-essential libssl-dev zlib1g-dev \
    libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
    libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev \
    libffi-dev uuid-dev libnss3-dev libgdbm-compat-dev && \
    wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz && \
    tar xzf Python-3.12.0.tgz && \
    cd Python-3.12.0 && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-3.12.0 Python-3.12.0.tgz && \
    python3.12 --version

# Create a symbolic link so that 'python3' points to 'python3.12'
RUN ln -sf /usr/local/bin/python3.12 /usr/bin/python3 && \
    python3 --version

# Install pip for Python 3.12 using ensurepip (bootstraps pip installation: 
# When building Python from source, pip is not included automatically — ensurepip installs it.).
# Then, create a symbolic link so 'pip' points to 'pip3.12'
RUN python3.12 -m ensurepip && \
    python3.12 -m pip install --upgrade pip && \
    ln -s /usr/local/bin/pip3.12 /usr/bin/pip

# Install the 'supervisor' process manager via pip.
# Supervisor is a python-based client/server system that allows its users to monitor and control a number of processes on UNIX-like operating systems.
# It is not meant to be run as a substitute for init as “process id 1”.
# Instead it is meant to be used to control processes related to a project or a customer.
RUN pip install supervisor

# Install project dependencies, without caching.
# --break-system-packages: used when installing packages into the system Python environment (e.g., /usr/local/lib/...) instead of a virtual environment.
# Normally, pip prevents overwriting system-installed packages to avoid breaking your OS-level tools. With --break-system-packages, you're telling pip
# to go ahead and install or overwrite packages in the system Python environment.
COPY Trustee_LLM/requirements-oldCPU.txt /opt/fastapi_app/
RUN pip install --break-system-packages --no-cache-dir -r /opt/fastapi_app/requirements-oldCPU.txt

# Copy FASTAPI application code inside /opt/fastapi_app/
COPY Trustee_LLM/app/ /opt/fastapi_app/app/
COPY Trustee_LLM/assets/ /opt/fastapi_app/assets/
COPY Trustee_LLM/config/ /opt/fastapi_app/config/
COPY Trustee_LLM/docs/ /opt/fastapi_app/docs/
COPY Trustee_LLM/frontend/ /opt/fastapi_app/frontend/
COPY Trustee_LLM/main.py /opt/fastapi_app/
COPY Trustee_LLM/README.md /opt/fastapi_app/

# Replace Apache virtual host configuration.
# Apache virtual host configuration can include:
# - DocumentRoot: specifies where to serve static files from
# - ProxyPass / ProxyPassReverse: to set up reverse proxying (e.g. to FastAPI on port 8000)
# - Logging configuration
# - Other Apache directives like authentication, access rules, etc.
# Without this step, Apache would use the default virtual host config,
# and would not forward requests to FastAPI — only serving static content under /opt/lampp/htdocs
COPY apache_proxy.conf /opt/lampp/etc/extra/httpd-vhosts.conf

# Add Supervisor configuration to manage Apache + FastAPI concurrently
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Enable Apache proxy modules and virtual host configuration.
# The following:
# - Uncomments a line in httpd.conf to enable mod_proxy: mod_proxy is an Apache module that provides proxy/gateway functionality,
#   enabling Apache to forward requests to other servers (e.g. to FastAPI app)
# - Uncomment the line loading mod_proxy_http.so, which enables HTTP protocol support within mod_proxy.
#   Without this module, Apache cannot proxy HTTP requests.
# - Uncomment the line that includes the virtual host configuration file,
#   allowing Apache to read and apply the custom virtual host rules
RUN sed -i '/mod_proxy.so/s/^#//g' /opt/lampp/etc/httpd.conf && \
    sed -i '/mod_proxy_http.so/s/^#//g' /opt/lampp/etc/httpd.conf && \
    sed -i 's|^#\s*\(Include etc/extra/httpd-vhosts.conf\)|\1|' /opt/lampp/etc/httpd.conf

# Expose Apache HTTP port
EXPOSE 80

# Start Supervisor (which manages both Apache and FastAPI processes), with its config file
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
