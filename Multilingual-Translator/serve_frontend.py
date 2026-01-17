"""
Simple HTTP server to serve the frontend
"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    os.chdir('frontend')
    port = 3000
    server = HTTPServer(('localhost', port), CORSRequestHandler)
    print(f'🚀 Frontend server running at http://localhost:{port}')
    print(f'📡 Backend API running at http://localhost:8000')
    print(f'\n✨ Open http://localhost:{port} in TWO browser windows to test!')
    print(f'   - Use the same room code in both windows')
    print(f'   - Select different languages for each user')
    print(f'   - Start chatting!\n')
    server.serve_forever()
