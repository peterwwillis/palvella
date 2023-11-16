#!/usr/bin/env sh
set -eu

# Background the app
DEBUG=1 python app.py & pid=$!
echo "pid $pid"
sleep 2

# Test /github_webhook
curl -X POST \
    -H "Content-Type: application/json" \
    -H "X-GitHub-Delivery: 72d3162e-cc78-11e3-81ab-4c9367dc0958" \
    -H "X-GitHub-Event: push" \
    -H "X-GitHub-Hook-ID: 292430182" \
    -H "X-Hub-Signature: 8800946b91b2d7b282ae8548d5b55e5cb8c6d4b8" \
    --data @./samples/github_webhook.json \
    http://localhost:8000/github_webhook

# Stop the app
kill $pid
wait
