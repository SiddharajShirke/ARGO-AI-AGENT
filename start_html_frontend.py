#!/usr/bin/env python3
"""
Simple HTTP server for the HTML frontend
This serves the static HTML file and handles CORS for API calls
"""
import http.server
import socketserver
import os
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def start_frontend_server(port=3005, directory="static"):
    """Start the HTML frontend server"""
    
    # Change to the directory containing the HTML files
    os.chdir(directory)
    
    print(f"""
🌐 HTML Frontend Server Starting
=====================================
🏠 Directory: {os.getcwd()}
🌐 URL: http://localhost:{port}
📁 Serving: index.html
🔗 Backend: http://localhost:8002

Open your browser and go to: http://localhost:{port}
Press Ctrl+C to stop the server
""")
    
    with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Frontend server stopped")

if __name__ == "__main__":
    import sys
    
    # Change to the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Check if static directory exists
    if not os.path.exists("static"):
        print("❌ Error: 'static' directory not found!")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    start_frontend_server()
