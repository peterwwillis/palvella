# syntax = docker/dockerfile:1.4

FROM pyenv:alpine-3.18-python-3.9 AS frontend-builder

WORKDIR /app
COPY requirements.txt ./

RUN --mount=type=cache,target=/root/.cache/pip pip -v install -r requirements.txt

COPY ./ /app/

# Allow the app to start its own web server(s)
CMD ["/app/app.py"]

# Uvicorn can use --interface option of 'auto', 'asgi3', 'asgi2', or 'wsgi'
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# WSGI
#CMD ["waitress-serve", "--host", "127.0.0.1", "--port", "8000", "frontend.main:app" ]


###########################################################################
FROM frontend-builder as frontend-dev-envs

RUN <<EOF
apt-get update
apt-get install -y --no-install-recommends git
EOF

RUN <<EOF
useradd -s /bin/bash -m vscode
groupadd docker
usermod -aG docker vscode
EOF
# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /
