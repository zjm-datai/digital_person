# base image
FROM python:3.13-slim-bookworm AS base

WORKDIR /app/api

# Install uv
ENV UV_VERSION=0.8.9

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com

RUN pip install --no-cache-dir uv=${UV_VERSION}

FROM base AS packages

RUN sed -i 's@deb.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --default-index https://pypi.tuna.tsinghua.edu.cn/simple

# production stage
FROM base AS production

ENV FLASK_APP=app.py
ENV DEPLOY_ENV=PRODUCTION

EXPOSE 5001

# set timezone
ENV TZ=UTC

# Set UTF-8 locale
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV PYTHONIOENCODING=utf-8

WORKDIR /app/api

# Create non-root user
ARG dp_uid=1001
RUN groupadd -r -g ${dp_uid} dp && \
    useradd -r -u ${dp_uid} -g ${dp_uid} -s /bin/bash dp && \
    chown -R dp:dp /app

# Copy Python environment and packages
ENV VIRTUAL_ENV=/app/api/.venv
COPY --from=packages --chown=dp:dp ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Copy source code
COPY --chown=dp:dp . /app/api/

# Prepare entrypoint script
COPY --chown=dp:dp --chmod=755 docker/entrypoint.sh /entrypoint.sh

USER dp

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]