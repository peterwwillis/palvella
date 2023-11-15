#!/usr/bin/env sh
set -eu

DEBUG=1 python app.py & pid=$!
echo "pid $pid"
sleep 3

curl -v -X POST -H "X-Hub-Signature: 8800946b91b2d7b282ae8548d5b55e5cb8c6d4b8" --data @./samples/github_webhook.json http://localhost:8000/github_webhook

kill $pid
