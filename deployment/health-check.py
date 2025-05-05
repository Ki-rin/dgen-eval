#!/usr/bin/env python3
"""
Health check endpoint for the Documentation Evaluation Dashboard.
This script runs alongside the Streamlit app and provides a simple HTTP endpoint
for health checking in container orchestration environments like OpenShift.
"""

import http.server
import socketserver
import threading
import os
import sys
import time
import requests
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("healthcheck")

# Constants
HEALTH_CHECK_PORT = int(os.environ.get('HEALTH_CHECK_PORT', 8081))
STREAMLIT_PORT = int(os.environ.get('STREAMLIT_SERVER_PORT', 8080))
STREAMLIT_HOST = os.environ.get('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for health check requests."""

    def do_GET(self):
        """Handle GET requests to the health check endpoint."""
        if self.path == '/health' or self.path == '/':
            try:
                # Try to connect to the Streamlit app
                response = requests.get(f'http://{STREAMLIT_HOST}:{STREAMLIT_PORT}/_stcore/health')
                
                if response.status_code == 200:
                    # Streamlit is running and healthy
                    self.send_response(200)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'OK - Service is healthy')
                else:
                    # Streamlit responded but with an error
                    self.send_response(503)
                    self.send_header('Content-type', 'text/plain')
                    self.end_headers()
                    self.wfile.write(b'Service is starting or unhealthy')
            except requests.RequestException:
                # Could not connect to Streamlit
                self.send_response(503)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Service is unavailable')
        else:
            # Path not found
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
        
        return
    
    def log_message(self, format, *args):
        """Override to use our logger instead of printing to stderr."""
        logger.info("%s - %s" % (self.address_string(), format % args))

def run_health_check_server():
    """Run the health check server in a separate thread."""
    with socketserver.TCPServer(("", HEALTH_CHECK_PORT), HealthCheckHandler) as httpd:
        logger.info(f"Health check server running on port {HEALTH_CHECK_PORT}")
        httpd.serve_forever()

def start_health_check():
    """Start the health check server in a background thread."""
    thread = threading.Thread(target=run_health_check_server, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    logger.info("Starting health check server...")
    thread = start_health_check()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down health check server...")
        sys.exit(0)
