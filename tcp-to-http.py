import http.server
import socketserver

PORT = 8000

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self): # Example: Handle GET requests (optional)
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Simple HTTP service is running (try a POST request)") # Send a simple message

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length) # Read data from the request body

        # Process the data (in this example, just echo it back)
        response_data = post_data  # Echo the received data

        self.send_response(200)  # OK status
        self.send_header("Content-type", "text/plain") # Or "application/json" if you want to send JSON
        self.end_headers()
        self.wfile.write(response_data) # Send the echoed data back

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving dynamic content at port {PORT}")
    httpd.serve_forever()