FROM tomsik68/xampp:latest

# Install Python3, pip, and supervisor
RUN apt-get update && \
    apt-get install -y python3 python3-pip supervisor && \
    rm -rf /var/lib/apt/lists/*

# Install FastAPI and Uvicorn
RUN pip3 install --break-system-packages fastapi uvicorn

# Copy FastAPI app code
COPY fastapi_app/ /opt/fastapi_app/

# Replace Apache virtual host configuration to enable proxy routes
COPY apache_proxy.conf /opt/lampp/etc/extra/httpd-vhosts.conf

# Add Supervisor configuration to manage Apache + FastAPI concurrently
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Enable Apache proxy modules and virtual host configuration
RUN sed -i '/mod_proxy.so/s/^#//g' /opt/lampp/etc/httpd.conf && \
    sed -i '/mod_proxy_http.so/s/^#//g' /opt/lampp/etc/httpd.conf && \
    sed -i 's|^#\s*\(Include etc/extra/httpd-vhosts.conf\)|\1|' /opt/lampp/etc/httpd.conf

# Expose Apache HTTP port
EXPOSE 80

# Start Supervisor (which manages both Apache and FastAPI processes)
CMD ["/usr/bin/supervisord"]
