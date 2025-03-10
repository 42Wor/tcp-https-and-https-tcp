import http.server
import socketserver
import socket
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '127.0.0.1'
PORT1 = 9999
PORT = 8000

class MyHandler(http.server.BaseHTTPRequestHandler):
    tcp_socket = None # Class-level socket, initialized to None
    connected_and_logged_in = False # Flag to track login status

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        response = {"message": "Simple HTTP service is running (try POST requests)"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        logging.info("GET request served.")

    def do_POST(self):
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
                logging.info(f"Forwarding data to TCP server (persistent connection): {post_data_json}")
                MyHandler.tcp_socket.sendall((json.dumps(post_data_json) + '\n').encode('utf-8'))

                data = self.recv_all(MyHandler.tcp_socket)
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

                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response_data_json).encode('utf-8'))
                logging.info("HTTP response sent to client.")

            except socket.error as tcp_e:
                logging.error(f"TCP Error during data exchange: {tcp_e}", exc_info=True)
                self.send_error_response(500, {"error": f"Error communicating with TCP server: {tcp_e}"})
                MyHandler.close_tcp_connection() # Close and reset on communication error

        except Exception as http_e:
            logging.error(f"HTTP Server Error in do_POST: {http_e}", exc_info=True)
            self.send_error_response(500, {"error": f"HTTP Server Error: {http_e}"})

    def send_error_response(self, status_code, error_message):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(error_message).encode('utf-8'))
        logging.error(f"HTTP Error Response sent: {error_message}")

    @classmethod
    def close_tcp_connection(cls):
        if cls.tcp_socket:
            cls.tcp_socket.close()
            logging.info("Persistent TCP connection closed.")
            cls.tcp_socket = None
            cls.connected_and_logged_in = False # Reset login flag

    @classmethod
    def server_close(cls, server): # Hook to close TCP on server shutdown
        logging.info("HTTP Server is closing...")
        cls.close_tcp_connection()
        server.server_close()

    def recv_all(self, sock, buffer_size=1024):
        data = b''
        while True:
            part = sock.recv(buffer_size)
            data += part
            if len(part) < buffer_size:
                break
        return data

def serve_forever_with_shutdown(server_address, handler_class):
    with socketserver.TCPServer(server_address, handler_class) as httpd:
        import signal
        def signal_handler(signum, frame):
            logging.info("Shutting down HTTP server...");
            handler_class.server_close(httpd) # Use the class method for shutdown
            httpd.shutdown()
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logging.info(f"Serving dynamic HTTP content, forwarding to TCP server at port {PORT1}, on HTTP port {PORT}")
        # Initialize TCP connection and login *before* starting to serve
        try:
            MyHandler.tcp_socket = socket.create_connection((HOST, PORT1))
            logging.info(f"Connected to TCP server at {HOST}:{PORT1}")
        except socket.error as e:
            logging.error(f"Failed to connect to TCP server at {HOST}:{PORT1}: {e}")
            return

        httpd.serve_forever()

if __name__ == "__main__":
    try:
        serve_forever_with_shutdown(("", PORT), MyHandler)
    except OSError as e:
        if e.errno == 98:
            logging.error(f"Port {PORT} is already in use. Please use a different port.")
        else:
            logging.error("OSError starting HTTP server:", exc_info=True)
            raise
    except Exception as e:
        logging.error("Unexpected error starting HTTP server:", exc_info=True)

        