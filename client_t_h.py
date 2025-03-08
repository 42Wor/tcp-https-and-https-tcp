import requests
import json
import time

#HTTP_SERVER_URL = 'http://127.0.0.1:8000'   Or your server's hostname/IP
HTTP_SERVER_URL = 'https://4d79-119-156-228-230.ngrok-free.app'

def send_data_to_http_server(data):
    """Sends JSON data to the HTTP server via a POST request and prints the response."""
    try:
        headers = {'Content-type': 'application/json'}
        response = requests.post(HTTP_SERVER_URL, json=data, headers=headers)
        response.raise_for_status()
        
        try:
            response_json = response.json()
            print(response_json)
        except json.JSONDecodeError:
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request Error: {e}")

if __name__ == "__main__":
    start=time.time()
    login_data = {"username": "testuser", "password": "testpassword", "databaseName": "mydatabase"}
    print(f"Sending login data to HTTP server: {login_data}")
    send_data_to_http_server(login_data)

    query_data_select = {"sql": "SELECT * FROM users;"} # Example SELECT query
    print(f"\nSending SELECT query to HTTP server: {query_data_select}")
    send_data_to_http_server(query_data_select)
    query_data_invalid_sql = {"sql": "SELEC * FROM users;"} # Example invalid SQL
    print(f"\nSending invalid SQL query to HTTP server: {query_data_invalid_sql}")
    send_data_to_http_server(query_data_invalid_sql)

 #   query_data_insert = {"sql": "INSERT INTO users (name, age) VALUES (?, ?);", "values": ["Alice", 30]} # Example INSERT query
   # print(f"\nSending INSERT query to HTTP server: {query_data_insert}")
  #  send_data_to_http_server(query_data_insert) 
    end=time.time()
    print(f"Time taken: {end-start}")
# This script sends login data and SQL queries to the HTTP server.