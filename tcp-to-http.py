import http.server
import socketserver
import socket
import json

HOST = '127.0.0.1'  # The server's hostname or IP address for the TCP server
PORT1 = 9999        # The port used by the TCP server
PORT = 8000         # The port for the HTTP server


class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):  # Example: Handle GET requests (optional)
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": "Simple HTTP service is running (try a POST request to forward data to TCP server)"}
        self.wfile.write(json.dumps(response).encode('utf-8'))  # Informative message

    def do_POST(self):
        try:
            # 1. Receive POST data from HTTP client
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)  # Read data from the request body
            try:
                post_data_json = json.loads(post_data.decode('utf-8'))  # Parse JSON data
            except json.JSONDecodeError as e:
                self.send_response(400)  # HTTP 400 Bad Request
                self.send_header("Content-type", "application/json")
                self.end_headers()
                error_message = {"error": f"Invalid JSON data: {e}"}
                self.wfile.write(json.dumps(error_message).encode('utf-8'))
                print(f"Invalid JSON data: {e}")  # Log the JSON error on server side
                return
            print(f"Received POST data: {post_data_json}")  # Log the POST data on server side

            # 2. Create a TCP socket and connect to the TCP server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.connect((HOST, PORT1))
                    print(f"Connected to TCP server at {HOST}:{PORT1}")
                    # 3. Forward the POST data to the TCP server
                    print(f"Forwarding POST data to TCP server: {post_data_json}")
                    s.sendall(json.dumps(post_data_json).encode('utf-8'))

                    # 4. Receive response from the TCP server
                    data = s.recv(1024)  # Receive up to 1024 bytes from TCP server
                    response_data = data.decode('utf-8')  # Use the data received from TCP server as HTTP response
                    response_data_json = json.loads(response_data)
                    print(f"Received response from TCP server: {response_data_json}")  # Log the TCP response on server side

                    # 5. Send HTTP 200 OK response with data from TCP server
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")  # Adjust content type as needed
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data_json).encode('utf-8'))  # Send the data received from TCP server back to HTTP client
                    s.close()  # Close the TCP connection
                    print("Connection to TCP server closed")

                except Exception as tcp_e:
                    # Handle exceptions during TCP communication
                    self.send_response(500)  # HTTP 500 Internal Server Error
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    error_message = {"error": f"Error communicating with TCP server: {tcp_e}"}
                    self.wfile.write(json.dumps(error_message).encode('utf-8'))
                    print(f"TCP Communication Error: {tcp_e}")  # Log the TCP error on server side

        except Exception as http_e:
            # Handle exceptions during HTTP request handling (e.g., reading request body)
            self.send_response(500)  # HTTP 500 Internal Server Error
            self.send_header("Content-type", "application/json")
            self.end_headers()
            error_message = {"error": f"HTTP Server Error: {http_e}"}
            self.wfile.write(json.dumps(error_message).encode('utf-8'))
            print(f"HTTP Server Error: {http_e}")  # Log the HTTP error on server side


if __name__ == "__main__":  # Standard practice to allow running as script
    try:
        with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
            print(f"Serving dynamic HTTP content, forwarding to TCP server at port {PORT1}, on HTTP port {PORT}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # errno 98 is for "Address already in use" (EADDRINUSE)
            print(f"Port {PORT} is already in use. Please use a different port.")
        else:
            raise  # Re-raise other OS errors