import http.client
import urllib.parse
import json 
import datetime

class HTTPPostClient:
    def __init__(self, host, port=80, timeout=10):
        self.host = host
        self.port = port 
        self.timeout = timeout
        self.connection = http.client.HTTPConnection(
            host = self.host,
            port = self.port,
            timeout = self.timeout
        )
    
    def post_form(self, path, data_dict, headers=None):
        if not isinstance(data_dict, dict):
            raise TypeError("data_dict must be a dictionary")
        
        encoded_data = urllib.parse.urlencode(data_dict)
        encoded_bytes = encoded_data.encode("utf-8")

        base_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(encoded_bytes)),
            "User-Agent": "Python-HTTP-POST-Client/2.0"
        }

        if headers:
            base_headers.update(headers)
        request_time = datetime.datetime.utcnow()

        self.connection.request(
            method="POST",
            url=path,
            body=encoded_bytes,
            headers=base_headers
        )

        response = self.connection.getresponse()
        response_body = response.read()

        result = {
            "timestamp_utc": request_time.isoformat(),
            "status": response.status,
            "reason": response.reason,
            "headers": dict(response.getheaders()),
            "body": response_body.decode(errors="ignore")
        }
        return result
    
    def close(self):
        self.connection.close

    

        