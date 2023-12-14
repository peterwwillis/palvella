#!/usr/bin/env sh
set -ux

_killstaleapp () {
    pkill -9 -fl "ython app.py"
}
_cleanup () {
    if [ -n "${res:-}" ] ; then
        if [ "$res" -ne 0 ] ; then
            kill -9 $pid
        else
            kill -15 $pid
        fi
    fi
    timeout 15s wait
    _killstaleapp
}

trap _cleanup EXIT SIGINT

#_killstaleapp

# Background the app
DEBUG=1 python app.py & pid=$!
echo "pid $pid"

# Test /github_webhook
curl -X POST \
    --connect-timeout 5 --max-time 5 \
    --silent \
    --retry 10 --retry-connrefused \
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
