import requests
import json
import time # Import time module

HTTP_SERVER_HOST = 'http://127.0.0.1' # Or your server's hostname/IP
HTTP_SERVER_PORT = 8000
HTTP_SERVER_URL = f"{HTTP_SERVER_HOST}:{HTTP_SERVER_PORT}"

def send_data_to_http_server(data, request_name="data"): # Added request_name for clarity
    """Sends JSON data to the HTTP server via a POST request and prints the response."""
    try:
        headers = {'Content-type': 'application/json'}
        print(f"Sending {request_name} to HTTP server: {data}") # More descriptive print
        response = requests.post(HTTP_SERVER_URL, json=data, headers=headers)

        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        print(f"HTTP Response Status Code ({request_name}): {response.status_code}") # Request name in output
        print("HTTP Response Headers:", response.headers)
        try:
            response_json = response.json()
            print(f"HTTP Response Body (JSON) - {request_name}:", response_json) # Request name in output
        except json.JSONDecodeError:
            print(f"HTTP Response Body (Text) - {request_name}:", response.text) # Request name in output

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request Error ({request_name}): {e}") # Request name in error

if __name__ == "__main__":
    login_data = {"username": "testuser", "password": "testpassword", "databaseName": "mydatabase"}
    send_data_to_http_server(login_data, "login data") # Send login and wait
    time.sleep(0.5) # Add a small delay to ensure server is ready (optional, but good practice)

    query_data_select = {"sql": "SELECT * FROM users;"} # Example SELECT query
    send_data_to_http_server(query_data_select, "SELECT query") # Send SELECT and wait
    time.sleep(0.5)

    query_data_insert = {"sql": "INSERT INTO users (name, age) VALUES (?, ?);", "values": ["Alice", 30]} # Example INSERT query
    send_data_to_http_server(query_data_insert, "INSERT query") # Send INSERT and wait
    time.sleep(0.5)

    query_data_invalid_sql = {"sql": "SELEC * FROM users;"} # Example invalid SQL
    send_data_to_http_server(query_data_invalid_sql, "invalid SQL query") # Send invalid SQL and wait
    time.sleep(0.5)