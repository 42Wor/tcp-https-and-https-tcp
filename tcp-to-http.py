import http.server
import socketserver
import socket
import json
import logging

# Configure logging for the HTTP server
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '127.0.0.1'  # TCP server hostname
PORT1 = 9999        # TCP server port
PORT = 8000         # HTTP server port

class MyHandler(http.server.BaseHTTPRequestHandler):

    tcp_socket = None  # Class-level variable to store the persistent TCP socket

    def do_GET(self):
        """Handles GET requests."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": "Simple HTTP service is running (try POST requests)"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        logging.info("GET request served.")

    def do_POST(self):
        """Handles POST requests, using a persistent TCP connection."""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                post_data_json = json.loads(post_data.decode('utf-8'))
                logging.info(f"Received POST data from HTTP client: {post_data_json}")
            except json.JSONDecodeError as e:
                self.send_error_response(400, {"error": f"Invalid JSON data from HTTP client: {e}"})
                logging.error(f"Invalid JSON data from HTTP client: {e}")
                return

            try:
                # 1. Ensure persistent TCP connection
                if MyHandler.tcp_socket is None:  # Check class-level socket
                    MyHandler.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create socket only once
                    MyHandler.tcp_socket.connect((HOST, PORT1)) # Connect once
                    logging.info(f"Established persistent connection to TCP server at {HOST}:{PORT1}")

                    # Send login data on initial connection (assuming first POST is login)
                    login_data = {"username": "testuser", "password": "testpassword", "databaseName": "mydatabase"} # Hardcoded login for simplicity - adjust as needed
                    logging.info(f"Sending login data to TCP server: {login_data}")
                    MyHandler.tcp_socket.sendall((json.dumps(login_data) + '\n').encode('utf-8'))

                    # Receive and check login response (important to confirm login success)
                    login_response_data = MyHandler.tcp_socket.recv(1024)
                    if not login_response_data:
                        raise socket.error("No login response from TCP server")
                    login_response_json = json.loads(login_response_data.decode('utf-8'))
                    logging.info(f"Received login response from TCP server: {login_response_json}")
                    if 'error' in login_response_json: # Check for error in login response
                        self.send_error_response(500, {"error": f"TCP Login Error: {login_response_json['error']}"})
                        return # Stop processing if login failed
                    else:
                         logging.info(f"TCP Login successful: {login_response_json.get('message') or login_response_json}")


                # 2. Forward POST data (query) to the persistent TCP connection
                logging.info(f"Forwarding data to TCP server (using persistent connection): {post_data_json}")
                MyHandler.tcp_socket.sendall((json.dumps(post_data_json) + '\n').encode('utf-8')) # Send query

                # 3. Receive response from TCP server
                data = MyHandler.tcp_socket.recv(1024)
                if not data:
                    logging.warning("No data received from TCP server.")
                    response_data_json = {"warning": "No response from TCP server"}
                else:
                    response_data = data.decode('utf-8')
                    try:
                        response_data_json = json.loads(response_data)
                        logging.info(f"Received response from TCP server: {response_data_json}")
                    except json.JSONDecodeError as e:
                        response_data_json = {"error": f"Invalid JSON response from TCP server: {e}", "raw_response": response_data}
                        logging.error(f"Invalid JSON response from TCP server: {e}, raw response: {response_data}")

                # 4. Send HTTP response back to client
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_data_json).encode('utf-8'))
                logging.info("HTTP response sent to client.")


            except socket.error as tcp_e:
                # Handle TCP socket errors, reset persistent connection
                logging.error(f"TCP Error: {tcp_e}", exc_info=True)
                self.send_error_response(500, {"error": f"Error communicating with TCP server: {tcp_e}"})
                MyHandler.tcp_socket = None # Reset persistent connection on error


        except Exception as http_e:
            # Handle HTTP server errors
            logging.error(f"HTTP Server Error: {http_e}", exc_info=True)
            self.send_error_response(500, {"error": f"HTTP Server Error: {http_e}"})


    def send_error_response(self, status_code, error_message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(error_message).encode('utf-8'))
        logging.error(f"HTTP Error Response sent: {error_message}")

    @classmethod
    def close_tcp_connection(cls):
        """Class method to close the persistent TCP connection when HTTP server stops."""
        if cls.tcp_socket:
            cls.tcp_socket.close()
            logging.info("Persistent TCP connection closed.")
            cls.tcp_socket = None


def serve_forever_with_shutdown(server_address, handler_class):
    """Sets up signal handlers for graceful shutdown and serves forever."""
    with socketserver.TCPServer(server_address, handler_class) as httpd:
        import signal
        def signal_handler(signum, frame):
            logging.info("Shutting down HTTP server...")
            handler_class.close_tcp_connection() # Close TCP connection on shutdown
            httpd.shutdown() # Initiate server shutdown
        signal.signal(signal.SIGINT, signal_handler) # Handle Ctrl+C
        signal.signal(signal.SIGTERM, signal_handler) # Handle termination signal

        logging.info(f"Serving dynamic HTTP content, forwarding to TCP server at port {PORT1}, on HTTP port {PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    try:
        serve_forever_with_shutdown(("", PORT), MyHandler) # Use modified serve_forever
    except OSError as e:
        if e.errno == 98:
            logging.error(f"Port {PORT} is already in use. Please use a different port.")
        else:
            logging.error("Error starting HTTP server:", exc_info=True)
            raise
    except Exception as e:
        logging.error("Unexpected error:", exc_info=True)