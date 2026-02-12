import http.client
import urllib.parse
import time
import threading
import http.server
import socketserver
import unittest
import json

# =========================
# HTTP CLIENT (PROCEDURAL)
# =========================

def http_get(host, path="/", port=80, timeout=5, headers=None):
    conn = http.client.HTTPConnection(host, port, timeout=timeout)

    final_headers = {
        "User-Agent": "Procedural-HTTP-Client/3.0",
        "Accept": "*/*",
        "Connection": "close"
    }

    if headers:
        final_headers.update(headers)

    start = time.perf_counter()

    conn.request("GET", path, headers=final_headers)
    response = conn.getresponse()
    body = response.read()

    end = time.perf_counter()
    conn.close()

    return {
        "status": response.status,
        "reason": response.reason,
        "headers": dict(response.getheaders()),
        "body": body.decode(errors="ignore"),
        "latency_ms": round((end - start) * 1000, 3)
    }


def http_post(host, path, data, port=80, timeout=5):
    encoded = urllib.parse.urlencode(data).encode()

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(encoded)),
        "User-Agent": "Procedural-HTTP-Client/3.0"
    }

    conn = http.client.HTTPConnection(host, port, timeout=timeout)
    conn.request("POST", path, body=encoded, headers=headers)

    response = conn.getresponse()
    body = response.read()

    conn.close()

    return {
        "status": response.status,
        "headers": dict(response.getheaders()),
        "body": body.decode(errors="ignore")
    }

# =========================
# MOCK HTTP SERVER
# =========================

class TestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        payload = {
            "path": self.path,
            "method": "GET"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode()

        payload = {
            "method": "POST",
            "received": body
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def log_message(self, *args):
        pass  # silence logs


def start_test_server(port):
    with socketserver.TCPServer(("localhost", port), TestHandler) as server:
        server.serve_forever()

# =========================
# UNIT TESTS
# =========================

class TestProceduralHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8090
        cls.server_thread = threading.Thread(
            target=start_test_server,
            args=(cls.port,),
            daemon=True
        )
        cls.server_thread.start()
        time.sleep(0.2)

    def test_http_get(self):
        res = http_get("localhost", "/", port=self.port)

        self.assertEqual(res["status"], 200)
        self.assertIn("latency_ms", res)
        self.assertIn("GET", res["body"])

    def test_http_post(self):
        res = http_post(
            "localhost",
            "/submit",
            {"x": "10", "y": "20"},
            port=self.port
        )

        self.assertEqual(res["status"], 200)
        self.assertIn("x=10", res["body"])
        self.assertIn("y=20", res["body"])

    def test_timeout(self):
        with self.assertRaises(Exception):
            http_get("10.255.255.1", "/", timeout=0.001)


if __name__ == "__main__":
    unittest.main()
