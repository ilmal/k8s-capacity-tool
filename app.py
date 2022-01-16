# modules
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# app files
from getCapacity import getCapacityFunc


def pathHandler(path, body):
    if "getCapacity" in path:
        return getCapacityFunc(body)


class main_server(BaseHTTPRequestHandler):
    def do_GET(self):
        body = ""
        if self.headers.get('Content-Length'):
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            body = json.loads(post_body)

        self.send_response(200)
        self.send_header('Content-type', 'json')
        self.end_headers()

        self.wfile.write(
            bytes(json.dumps(pathHandler(self.path, body)), "utf8"))


def main():
    PORT = 3000
    server = HTTPServer(("", PORT), main_server)
    print("Server running on port: ", PORT)
    server.serve_forever()


main()
