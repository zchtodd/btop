#!/usr/bin/env python

if __name__ == "__main__":
    import os
    import time
    import socketserver
    import webbrowser
    import btop

    from http.server import SimpleHTTPRequestHandler
    from multiprocessing import Process

    def run_http_server():
        package_root = os.path.dirname(os.path.abspath(btop.__file__))
        os.chdir(os.path.join(package_root, "data"))

        httpd = socketserver.TCPServer(("localhost", 3120), SimpleHTTPRequestHandler)
        httpd.serve_forever()

    def run_sock_server():
        server = btop.BtopServer(5678)
        server.start()

    http_server_proc = Process(target=run_http_server)
    sock_server_proc = Process(target=run_sock_server)

    http_server_proc.start()
    sock_server_proc.start()

    time.sleep(3)
    webbrowser.open("http://localhost:3120")
