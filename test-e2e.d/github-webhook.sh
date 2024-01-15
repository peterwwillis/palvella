#!/usr/bin/env sh
set -eu
[ "${DEBUG:-0}" = "1" ] && set -x

trap _cleanup EXIT SIGINT

_run_app

# Test /github_webhook
_run_curl_post \
    -H "Content-Type: application/json" \
    -H "X-GitHub-Delivery: 72d3162e-cc78-11e3-81ab-4c9367dc0958" \
    -H "X-GitHub-Event: push" \
    -H "X-GitHub-Hook-ID: 292430182" \
    -H "X-Hub-Signature: a2861cc69fde2fe3b05881da454bb32ceedef810" \
    -H "X-Hub-Signature-256: eeb44e7fea56b550d865f167e467bc755a0fb3713da822924a79d4a423749d37" \
    --data-binary @./samples/github_webhook.json \
    http://localhost:8000/github_webhook
res=$?

sleep 4
