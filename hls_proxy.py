#!/usr/bin/env python3
"""HLS 代理服务器（多线程）：4000 端口 → /hls/* → MediaMTX :8888，/* → 静态文件"""
import http.server
import socketserver
import urllib.request
import os
import sys

PORT = 4000
TARGET_HOST = 'http://localhost:8888'

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """多线程 HTTP 服务器，支持并发请求"""
    daemon_threads = True

class HLSProxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/hls/'):
            hls_path = self.path[4:]  # 去掉 /hls 前缀
            url = f'{TARGET_HOST}{hls_path}'
            try:
                req = urllib.request.Request(url, headers={
                    'User-Agent': 'HLS-Proxy/1.0'
                })
                with urllib.request.urlopen(req, timeout=5) as resp:
                    body = resp.read()
                    self.send_response(200)
                    ct = resp.headers.get('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Type', ct)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Cache-Control', 'no-store')
                    self.send_header('Content-Length', str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'HLS proxy error: {e}'.encode())
        elif self.path == '/':
            self.send_response(302)
            self.send_header('Location', '/yolov26-rtsp-detection.html')
            self.end_headers()
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        pass  # 静默日志，减少输出

if __name__ == '__main__':
    os.chdir('/Users/paocai/WorkBuddy/2026-05-19-task-13')
    httpd = ThreadingHTTPServer(('', PORT), HLSProxy)
    print(f'HLS Proxy (multi-threaded) on http://localhost:{PORT}')
    sys.stdout.flush()
    httpd.serve_forever()
