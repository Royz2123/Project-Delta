import http.server
import socketserver
import threading
import time
import get_diffs

PORT = 8080

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    threading.Thread(target=httpd.serve_forever).start()

    get_diffs.run_session("outdoor4")

    while True:
        time.sleep(2)
