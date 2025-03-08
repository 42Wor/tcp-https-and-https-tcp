import http.server
import socketserver
import socket
import json
import logging

# Configure logging for the HTTP server (optional, but good practice)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '127.0.0.1'  # The server's hostname or IP address for the TCP server
PORT1 = 9999        # The port used by the TCP server
PORT = 8000         # The port for the HTTP server

class MyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Handles GET requests. Returns a simple message indicating the service is running."""
        self.send_response(200)  # HTTP OK status
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": "Simple HTTP service is running (try a POST request to forward data to TCP server)"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        logging.info("GET request served.")

    def do_POST(self):
        """Handles POST requests. Forwards JSON data to a TCP server and returns the TCP server's response."""
        try:
            # 1. Receive POST data from HTTP client
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)  # Read data from the request body

            try:
                post_data_json = json.loads(post_data.decode('utf-8'))  # Parse JSON data
                logging.info(f"Received POST data from HTTP client: {post_data_json}")
            except json.JSONDecodeError as e:
                self.send_response(400)  # HTTP 400 Bad Request
                self.send_header("Content-type", "application/json")
                self.end_headers()
                error_message = {"error": f"Invalid JSON data received from HTTP client: {e}"}
                self.wfile.write(json.dumps(error_message).encode('utf-8'))
                logging.error(f"Invalid JSON data from HTTP client: {e}")
                return  # Exit the handler if JSON is invalid

            # 2. Create a TCP socket and connect to the TCP server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
                try:
                    tcp_socket.connect((HOST, PORT1))
                    logging.info(f"Successfully connected to TCP server at {HOST}:{PORT1}")

                    # 3. Forward the POST data to the TCP server
                    logging.info(f"Forwarding data to TCP server: {post_data_json}")
                    tcp_socket.sendall(json.dumps(post_data_json).encode('utf-8'))

                    # 4. Receive response from the TCP server
                    data = tcp_socket.recv(1024)  # Receive up to 1024 bytes from TCP server
                    if not data:
                        logging.warning("No data received from TCP server.")
                        response_data_json = {"warning": "No response from TCP server"} # Handle empty TCP response
                    else:
                        response_data = data.decode('utf-8')
                        try:
                            response_data_json = json.loads(response_data)
                            logging.info(f"Received response from TCP server: {response_data_json}")
                        except json.JSONDecodeError as e:
                            response_data_json = {"error": f"Invalid JSON response from TCP server: {e}", "raw_response": response_data}
                            logging.error(f"Invalid JSON response from TCP server: {e}, raw response: {response_data}")

                    # 5. Send HTTP 200 OK response with data from TCP server
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data_json).encode('utf-8'))
                    logging.info("HTTP response sent to client with data from TCP server.")

                except socket.error as tcp_e:
                    # Handle TCP connection or communication errors
                    self.send_response(500)  # HTTP 500 Internal Server Error
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    error_message = {"error": f"Error communicating with TCP server: {tcp_e}"}
                    self.wfile.write(json.dumps(error_message).encode('utf-8'))
                    logging.error(f"TCP Communication Error: {tcp_e}")

        except Exception as http_e:
            # Handle any other exceptions during HTTP request processing
            self.send_response(500)  # HTTP 500 Internal Server Error
            self.send_header("Content-type", "application/json")
            self.end_headers()
            error_message = {"error": f"HTTP Server Error: {http_e}"}
            self.wfile.write(json.dumps(error_message).encode('utf-8'))
            logging.error(f"HTTP Server Error: {http_e}", exc_info=True) # Log with traceback for debugging


if __name__ == "__main__":
    try:
        with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
            logging.info(f"Serving dynamic HTTP content, forwarding to TCP server at port {PORT1}, on HTTP port {PORT}")
            httpd.serve_forever()
    except OSError as e:
        if e.errno == 98:  # errno 98 is for "Address already in use" (EADDRINUSE)
            logging.error(f"Port {PORT} is already in use. Please use a different port.")
        else:
            logging.error("Error starting HTTP server:", exc_info=True) # Log other OS errors with traceback
            raise # Re-raise other OS errors
    except Exception as e:
        logging.error("Unexpected error:", exc_info=True) # Catch any other top-level exceptions