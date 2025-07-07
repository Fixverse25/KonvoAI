#!/usr/bin/env python3
"""
Simple HTTP server for KonvoAI frontend development
Serves the frontend with proper CORS headers for local testing
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with CORS support"""
    
    def end_headers(self):
        """Add CORS headers to all responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight OPTIONS requests"""
        self.send_response(200)
        self.end_headers()

def main():
    """Start the development server"""
    # Change to the public directory
    public_dir = Path(__file__).parent / 'public'
    if not public_dir.exists():
        print(f"Error: Public directory not found at {public_dir}")
        sys.exit(1)
    
    os.chdir(public_dir)
    
    # Server configuration
    PORT = 3000
    HOST = 'localhost'
    
    # Start server
    with socketserver.TCPServer((HOST, PORT), CORSHTTPRequestHandler) as httpd:
        print(f"🚀 KonvoAI Frontend Server")
        print(f"📍 Serving at: http://{HOST}:{PORT}")
        print(f"📁 Directory: {public_dir}")
        print(f"🔗 Open: http://{HOST}:{PORT}")
        print(f"⏹️  Press Ctrl+C to stop")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n🛑 Server stopped")

if __name__ == "__main__":
    main()
