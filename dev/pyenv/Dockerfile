FROM alpine:3.18.4 AS base

ENV LANGUAGE en_US:en
ENV LANG C.UTF-8
ENV CHARSET UTF-8
ENV LC_ALL C.UTF-8
ENV LC_COLLATE C.UTF-8
ENV TZ=UTC
RUN apk add musl-locales tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ARG PYENV_INSTALL_VERSION
WORKDIR /src
COPY --chmod=0755 pyenvrc* Makefile /src/pyenv/
RUN cd /src/pyenv \
    && . ./pyenvrc

ENV HOME /root
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH
