from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Event, Thread

import infernux as inx


class HelloHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        body = b"Hello from my plugin!"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args) -> None:
        pass


class HelloPreload(inx.InxPreload):
    def preload(self, context: inx.PreloadContext) -> None:
        server = HTTPServer(("127.0.0.1", 0), HelloHandler)
        context.add_cleanup(server.server_close)
        server.timeout = 0.1
        stopping = Event()

        def serve() -> None:
            while not stopping.is_set():
                server.handle_request()

        worker = Thread(target=serve, name="hello-plugin-http", daemon=True)

        def stop() -> None:
            stopping.set()
            worker.join(timeout=1.0)
            if worker.is_alive():
                raise RuntimeError("Hello Plugin HTTP worker did not stop")

        worker.start()
        context.add_cleanup(stop)
        inx.Debug.log(f"Hello service: http://127.0.0.1:{server.server_port}")
