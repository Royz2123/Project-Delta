import http.server
import socketserver
import threading

import get_diffs

PORT = 8000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    threading.Thread(target=httpd.serve_forever).start()

    get_diffs.run_session()