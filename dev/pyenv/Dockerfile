FROM alpine:3.18.4 AS base

ENV LANG=POSIX
ENV LANGUAGE=POSIX
ENV LC_ALL=POSIX
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone


WORKDIR /src
COPY --chmod=0755 pyenvrc* Makefile /src/pyenv/
RUN cd /src/pyenv && . ./pyenvrc
