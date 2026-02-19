"""
Фронтенд-сервер без кеширования (для разработки).
Запуск: python serve.py
Браузер будет получать свежие файлы при каждой загрузке.
"""
import http.server
import socketserver

PORT = 5500


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


with socketserver.TCPServer(("", PORT), NoCacheHandler) as httpd:
    print(f"Serving HTTP on port {PORT} (no-cache) http://127.0.0.1:{PORT}/")
    httpd.serve_forever()
