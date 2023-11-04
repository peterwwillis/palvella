# syntax = docker/dockerfile:1.4

FROM python:3.9 AS frontend-builder

WORKDIR /app
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip pip -v install -r requirements.txt

COPY ./frontend /app/frontend

CMD ["uvicorn", "frontend.main:asgi_app", "--host", "0.0.0.0", "--port", "8000", "--reload"]



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
