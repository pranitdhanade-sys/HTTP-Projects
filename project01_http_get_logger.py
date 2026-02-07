import http.client
import datetime

class HTTPGetLogger:
    def __init__(self,host,port=80,timeout=10):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.connection = http.client.HTTPConnection(
            host=self.host,
            port=self.port,
            timeout=self.timeout
        )
    def fetch(self,path="/"):
        request_time = datetime.datetime.utcnow()

        self.connection.request(
            method="GET",
            url=path,
            headers={
                "User-Agent":"Python-HTTP-Logger/1.0",
                "Accept":"*/*"
            }
        )
        response = self.connection.getresponse()
        body = response.read()

        log = {
            "timestamp_utc": request_time.isoformat(),
            "host": self.host,
            "path": path,
            "status_code": response.status,
            "reason": response.reason,
            "headers": dict(response.getheaders()),
            "response_size_bytes": len(body)
        }
        return log
    
    def close(self):
        self.connection.close

if __name__ == "__main__":
    logger = HTTPGetLogger("example.com")

    result = logger.fetch("/")

    print("\n===HTTP GET LOG===")
    for key,value in result.items():
        print(f"{key}:{value}")

    logger.close()
