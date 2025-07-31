import socketserver

class MyHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        print(f"Reçu: {data}")
        self.request.sendall("Bien reçu".encode("utf-8"))

def start_server(port=8000):
    with socketserver.TCPServer(("0.0.0.0", port), MyHandler) as server:
        print(f"Serveur en écoute sur le port {port}...")
        server.serve_forever()
