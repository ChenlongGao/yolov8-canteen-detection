#!/usr/bin/env node
/**
 * HLS 代理服务器 (Node.js)
 * 端口 4000: 静态文件 + HLS 流代理到 MediaMTX :8888
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 4000;
const ROOT = '/Users/paocai/WorkBuddy/2026-05-19-task-13';
const HLS_TARGET = 'http://127.0.0.1:8888';

function contentType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const types = {
    '.html': 'text/html; charset=utf-8',
    '.css': 'text/css',
    '.js': 'application/javascript',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.mp4': 'video/mp4',
    '.m3u8': 'application/vnd.apple.mpegurl',
    '.ts': 'video/mp2t',
    '.mp3': 'audio/mpeg',
  };
  return types[ext] || 'application/octet-stream';
}

const server = http.createServer((req, res) => {
  const url = req.url.split('?')[0];

  // HLS 代理：转发到 MediaMTX
  if (url.startsWith('/hls/')) {
    const targetPath = url.slice(4); // 去掉 /hls
    const targetUrl = `${HLS_TARGET}${targetPath}`;

    const proxy = http.get(targetUrl, (proxyRes) => {
      res.writeHead(proxyRes.statusCode, {
        'Content-Type': proxyRes.headers['content-type'] || 'application/octet-stream',
        'Access-Control-Allow-Origin': '*',
        'Cache-Control': 'no-store',
      });
      proxyRes.pipe(res);
    });

    proxy.on('error', (err) => {
      res.writeHead(502);
      res.end('HLS proxy error: ' + err.message);
    });

    proxy.setTimeout(30000, () => {
      proxy.destroy();
      res.writeHead(504);
      res.end('HLS proxy timeout');
    });

    return;
  }

  // 首页重定向
  if (url === '/') {
    res.writeHead(302, { 'Location': '/yolov26-rtsp-detection.html' });
    res.end();
    return;
  }

  // 静态文件
  const filePath = path.join(ROOT, url);
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('Not Found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType(filePath), 'Cache-Control': 'no-cache' });
    res.end(data);
  });
});

server.listen(PORT, () => {
  console.log(`HLS Proxy (Node.js) on http://localhost:${PORT}`);
  console.log(`  /hls/*  →  ${HLS_TARGET}/*`);
  console.log(`  /*      →  static files from ${ROOT}`);
});
