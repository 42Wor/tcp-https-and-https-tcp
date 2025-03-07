import socket
import time
import traceback  # For detailed error information

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 12345        # Port to listen on (non-privileged ports are > 1023)

def handle_client(conn, addr):
    """Handles communication with a single client."""
    print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(1024)  # Receive up to 1024 bytes
            if not data:
                # Client disconnected gracefully (sent 0 bytes)
                print(f"Client {addr} disconnected gracefully.")
                break  # Exit the loop, client is done
            try:
                decoded_data = data.decode('utf-8') # Explicitly decode as UTF-8, handle potential errors
                print(f"Received from {addr}: {decoded_data}")
            except UnicodeDecodeError:
                decoded_data = repr(data) # If decoding fails, show raw bytes representation
                print(f"Received non-UTF-8 data from {addr}: {decoded_data}")

            try:
                conn.sendall(data)  # Send back the received data (echo)
            except socket.error as e:
                print(f"Error sending data to {addr}: {e}")
                break # Stop communication if send fails

    except ConnectionResetError:
        print(f"Connection reset by client {addr}") # Client abruptly disconnected
    except Exception as e: # Catch any other exceptions during client handling
        print(f"Error handling client {addr}: {e}")
        traceback.print_exc() # Print full traceback for debugging
    finally:
        conn.close() # Ensure connection is always closed
        print(f"Connection with {addr} closed.")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        print(f"Error binding socket: {e}")
        exit(1) # Exit if binding fails, server cannot start

    s.listen()
    print(f"Listening on {HOST}:{PORT}...")

    while True: # Keep accepting new connections in a loop
        try:
            conn, addr = s.accept() # Accept incoming connection
            handle_client(conn, addr) # Call function to handle client communication
        except KeyboardInterrupt: # Allow graceful shutdown with Ctrl+C
            print("Server shutting down...")
            break # Exit the main loop and server will close
        except socket.error as e:
            print(f"Socket accept error: {e}") # Handle accept errors, but keep server running
            continue # Go back to listening for new connections
        except Exception as e: # Catch any other errors during accept loop
            print(f"Unexpected error during accept: {e}")
            traceback.print_exc() # Print full traceback for debugging
            continue # Try to continue accepting new connections

print("Server stopped.")