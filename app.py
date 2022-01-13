# modules
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# app files
from getCapacity import getCapacityFunc


def pathHandler(path, body):
    if "getCapacity" in path:
        getCapacityFunc(body)


class main_server(BaseHTTPRequestHandler):
    def do_GET(self):
        body = ""
        if self.headers.get('Content-Length'):
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            body = json.loads(post_body)

        pathHandler(self.path, body)


def main():
    PORT = 3000
    server = HTTPServer(("", PORT), main_server)
    print("Server running on port: ", PORT)
    server.serve_forever()


main()
