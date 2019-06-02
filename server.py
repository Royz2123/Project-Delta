import http.server
import socketserver
import threading
import time
import get_diffs
import create_session

try:
    import imageio
    imageio.plugins.ffmpeg.download()
except:
    pass

PORT = 7000

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    threading.Thread(target=httpd.serve_forever).start()
    threading.Thread(target=get_diffs.run_session, args=("outdoor4", False)).start()
    # threading.Thread(target=create_session.main).start()

    while True:
        print("yo")
        time.sleep(2)
