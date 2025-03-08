import requests
import json

HTTP_SERVER_HOST = 'http://127.0.0.1' # Or your server's hostname/IP
HTTP_SERVER_PORT = 8000
HTTP_SERVER_URL = f"{HTTP_SERVER_HOST}:{HTTP_SERVER_PORT}"

def send_data_to_http_server(data):
    """Sends JSON data to the HTTP server via a POST request and prints the response."""
    try:
        headers = {'Content-type': 'application/json'}
        response = requests.post(HTTP_SERVER_URL, json=data, headers=headers) # Use json=data for requests lib

        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        print(f"HTTP Response Status Code: {response.status_code}")
        print("HTTP Response Headers:", response.headers)
        try:
            response_json = response.json()
            print("HTTP Response Body (JSON):", response_json)
        except json.JSONDecodeError:
            print("HTTP Response Body (Text):", response.text) # If not JSON, print as text

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request Error: {e}")

if __name__ == "__main__":
    login_data = {"username": "testuser", "password": "testpassword", "databaseName": "mydatabase"}
    print(f"Sending login data to HTTP server: {login_data}")
    send_data_to_http_server(login_data)

    query_data_select = {"sql": "SELECT * FROM users;"} # Example SELECT query
    print(f"\nSending SELECT query to HTTP server: {query_data_select}")
    send_data_to_http_server(query_data_select)

    query_data_insert = {"sql": "INSERT INTO users (name, age) VALUES (?, ?);", "values": ["Alice", 30]} # Example INSERT query
    print(f"\nSending INSERT query to HTTP server: {query_data_insert}")
    send_data_to_http_server(query_data_insert)

    query_data_invalid_sql = {"sql": "SELEC * FROM users;"} # Example invalid SQL
    print(f"\nSending invalid SQL query to HTTP server: {query_data_invalid_sql}")
    send_data_to_http_server(query_data_invalid_sql)