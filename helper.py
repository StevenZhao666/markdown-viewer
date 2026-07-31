#!/usr/bin/env python3
"""文件读写小助手 — 给 MarkdownViewer 提供本地文件读写能力"""

import http.server
import json
import urllib.parse
import sys
import os
import socketserver

PORT = 18520
VIEWER_PATH = r'D:\MarkdownViewer\viewer.html'
ROOT_DIR = r'D:\MarkdownViewer'


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path == '/':
            self._serve_viewer()
        elif parsed.path == '/api/read':
            path = params.get('path', [None])[0]
            if not path:
                return self._json({'error': 'missing path'}, 400)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self._json({'content': content, 'path': path})
            except Exception as e:
                self._json({'error': str(e)}, 500)
        elif parsed.path == '/api/ping':
            self._json({'ok': True})
        elif parsed.path == '/api/shutdown':
            self._json({'ok': True})
            import threading
            threading.Thread(target=self.server.shutdown).start()
        else:
            # 尝试映射到 ROOT_DIR 下的静态文件（防路径逃逸）
            local = os.path.normpath(os.path.join(ROOT_DIR, parsed.path.lstrip('/')))
            real_local = os.path.realpath(local)
            real_root = os.path.realpath(ROOT_DIR)
            if os.path.commonpath([real_local, real_root]) == real_root:
                try:
                    with open(local, 'rb') as f:
                        data = f.read()
                    ext = os.path.splitext(local)[1].lower()
                    ct = {'.js':'application/javascript','.css':'text/css',
                          '.woff2':'font/woff2','.woff':'font/woff',
                          '.html':'text/html','.json':'application/json'}.get(ext,'application/octet-stream')
                    self._ok(ct, data)
                except FileNotFoundError:
                    self._json({'error': 'not found'}, 404)
            else:
                self._json({'error': 'forbidden'}, 403)

    def do_POST(self):
        if self.path == '/api/write':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            path = body.get('path', '')
            content = body.get('content', '')
            if not path:
                return self._json({'error': 'missing path'}, 400)
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._json({'ok': True, 'path': path})
            except Exception as e:
                self._json({'error': str(e)}, 500)
        else:
            self._json({'error': 'not found'}, 404)

    def _serve_viewer(self):
        try:
            with open(VIEWER_PATH, 'r', encoding='utf-8') as f:
                html = f.read()
            self._ok('text/html; charset=utf-8', html.encode('utf-8'), headers={'Cache-Control':'no-cache,no-store,must-revalidate'})
        except FileNotFoundError:
            self._json({'error': 'MarkdownViewer.html not found at ' + VIEWER_PATH}, 404)

    def _json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self._ok('application/json', body, status)

    def _ok(self, content_type, body, status=200, headers=None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(body)))
        if headers:
            for k,v in headers.items():
                self.send_header(k,v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # 安静运行，不刷屏


def main():
    server = socketserver.ThreadingTCPServer(('127.0.0.1', PORT), Handler)
    print(f'FILE_HELPER_READY port={PORT}', flush=True)
    server.serve_forever()


if __name__ == '__main__':
    main()
