#!/bin/bash
set -e

[ -d "web" ] && cd web || { echo "web 目录不存在"; exit 1; }

npm run build

[ -d "dist" ] || { echo "构建产物 dist 目录不存在"; exit 1; }

rm -rf /data/services/maas/volumes/nginx-80/html/consultation
mv dist /data/services/maas/volumes/nginx-80/html/consultation