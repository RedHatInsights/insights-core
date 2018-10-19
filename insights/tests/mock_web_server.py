import sys
from threading import Thread
import socket

if (sys.version_info > (3, 0)):
    from http.server import BaseHTTPRequestHandler, HTTPServer
else:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


SERVER_PORT = get_free_port()


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        print(self.path)
        value = ''
        send_reply = False
        if self.path.endswith("/mock"):
            send_reply = True

        value = "text/json"

        if send_reply:
            self.send_response(200)
            self.send_header('Content-type', value)
            self.end_headers()
            output = ""
            output += '{"data":{"id": "001", "name": "Successful return from Mock Service"}}'
            self.wfile.write(output.encode(encoding='utf_8'))
            print (output)
            return
        else:
            self.send_response(404)
            self.send_header('Content-type', value)
            self.end_headers()
            output = ""
            output += '{"error":{"code": "404", "message": "Not Found"}}'
            self.wfile.write(output.encode(encoding='utf_8'))
            print (output)
            return
        return


class TestMockServer(object):

    server_port = 8080

    @classmethod
    def setup_class(self):
        self.server_port = get_free_port()
        self.mock_server_port = get_free_port()
        self.mock_server = HTTPServer(('localhost', self.server_port), RequestHandler)

        # Start running mock server in a separate thread.
        # Daemon threads automatically shut down when the main process exits.
        self.mock_server_thread = Thread(target=self.mock_server.serve_forever)
        self.mock_server_thread.setDaemon(True)
        self.mock_server_thread.start()

    def get_server_port(self):

        return self.server_port
