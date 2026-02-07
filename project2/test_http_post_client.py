import unittest
import threading
import http.server
import socketserver
import json
from http_post_client import HTTPPostClient

class TestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int (self.headers.get("Content-Length",0))
        post_data = self.rfile.read(content_length).decode()

        response = {
            "recieved":post_data,
            "path":self.path
        }

        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.end_headers()
        self.wfil.write(json.dumps(response).encode())

    def log_message(self, *args):
        #return super().log_message(format, *args)
        pass

def start_test_server(port):
    with socketserver.TCPServer(("localhost", port),TestHandler) as httpd:
        http.serve_forever()

class HTTPPostClienTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8080
        cls.server_thread = threading.Thread(
            target = start_test_server,
            args = (cls.port,),
            daemon=True
        )
        cls.server_thread.start()

    def test_post_form_success(self):
        client = HTTPPostClient("localhost",port=self.port)

        response = client.post_form(
            "/submit",
            {"name":"test", "value":"123"}
        )

        self.assertEqual(response["status",200])
        self.assertIn("name=test", response["body"])
        self.assertIn("value=123", response["body"])
        
        client.close()

    def test_invalid_data_type(self):
        client = HTTPPostClient("localhost", port=self.port)

        with self.assertRaises(TypeError):
            client.post_form("/submit","invalid")

        client.close()

if __name__ == "__main__":
    unittest.main()