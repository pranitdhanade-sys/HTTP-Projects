import socket
import threading
import urllib.parse
import time

# =========================
# RAW SOCKET HTTP SERVER
# =========================

HOST = "127.0.0.1"
PORT = 9000

def handle_client(conn, addr):
    try:
        request = conn.recv(4096).decode()
        lines = request.split("\r\n")
        request_line = lines[0] if lines else ""
        method, path, _ = request_line.split() if request_line else ("", "", "")
        
        print(f"[SERVER] {addr} requested {method} {path}")
        
        if method == "GET":
            body = f"Hello! You requested {path}"
        elif method == "POST":
            headers_end = request.find("\r\n\r\n")
            body = request[headers_end+4:] if headers_end != -1 else ""
            body = f"POST body received: {body}"
        else:
            body = f"Method {method} not supported"

        response = "HTTP/1.1 200 OK\r\n"
        response += f"Content-Length: {len(body.encode())}\r\n"
        response += "Content-Type: text/plain\r\n\r\n"
        response += body

        conn.sendall(response.encode())
    except Exception as e:
        print(f"[SERVER ERROR] {e}")
    finally:
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    while True:
        client_conn, client_addr = server.accept()
        threading.Thread(target=handle_client, args=(client_conn, client_addr), daemon=True).start()


# =========================
# RAW SOCKET HTTP CLIENT
# =========================

def raw_http_get(host, port, path="/"):
    with socket.create_connection((host, port), timeout=5) as sock:
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock.sendall(request.encode())
        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    header, _, body = response.partition(b"\r\n\r\n")
    return header.decode(), body.decode()


def raw_http_post(host, port, path, data_dict):
    body_data = urllib.parse.urlencode(data_dict)
    with socket.create_connection((host, port), timeout=5) as sock:
        request = f"POST {path} HTTP/1.1\r\nHost: {host}\r\n"
        request += f"Content-Type: application/x-www-form-urlencoded\r\n"
        request += f"Content-Length: {len(body_data.encode())}\r\n"
        request += "Connection: close\r\n\r\n"
        request += body_data
        sock.sendall(request.encode())

        response = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
    header, _, body = response.partition(b"\r\n\r\n")
    return header.decode(), body.decode()


# =========================
# RUN SERVER + CLIENT DEMO
# =========================

if __name__ == "__main__":
    # Start server in background
    threading.Thread(target=start_server, daemon=True).start()
    time.sleep(0.5)  # give server time to start

    # GET request demo
    headers, body = raw_http_get(HOST, PORT, "/hello")
    print("\n=== GET REQUEST ===")
    print(headers)
    print(body)

    # POST request demo
    headers, body = raw_http_post(HOST, PORT, "/submit", {"x": "123", "y": "456"})
    print("\n=== POST REQUEST ===")
    print(headers)
    print(body)
