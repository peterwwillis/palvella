#!/usr/bin/env sh
set -ux
[ "${DEBUG:-0}" = "1" ] && set -x


_killstaleapp () {
    pkill -9 -f "ython app.py"
}
_cleanup () {
    if [ -n "${res:-}" ] ; then
        if [ "$res" -ne 0 ] ; then
            kill -9 $pid
        else
            kill -15 $pid
        fi
    fi
    _killstaleapp
}
_run_app () {
    # Background the app
    DEBUG=1 python app.py & pid=$!
    echo "$pid"
}
_run_curl_post () {
    curl -X POST \
        --connect-timeout 5 --max-time 5 \
        --silent \
        --retry 10 --retry-connrefused \
        "$@"
}


for script in ./test-e2e.d/*.sh ; do
    ( . "$script" )
done
