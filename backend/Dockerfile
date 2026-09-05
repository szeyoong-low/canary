FROM python:3.12-slim

# Run all commands from this directory instead of filesystem root
WORKDIR /backend

# Copies the uv binary directly from the official image instead of pip installing
COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /usr/local/bin/uv

# Amazon's RDS root certificates for every region. RDS refuses IAM
# authentication over an unencrypted connection, and the application verifies
# the server against this bundle rather than the operating system's trust store,
# which would accept any certificate a public CA issued for the endpoint's name.
#
# `ADD` fetches the URL itself. The base image has no curl or wget.
#
# Deliberately not pinned with `--checksum`: AWS rotates the bundle as regional
# CAs are added, so a pin would break the build on their schedule rather than
# ours. The trust here is TLS to amazonaws.com at build time.
# https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html
ADD --chmod=644 https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem \
    /etc/ssl/certs/rds-global-bundle.pem

# Docker caches each instruction as a layer, so code-only changes won't
# re-download dependency packages
COPY pyproject.toml uv.lock ./

# Sync without automatically updating the lock file to ensure reproducibility.
# This is equivalent to `npm ci`.
RUN uv sync --frozen --no-dev

# Copy source files from current directory on host to container working directory
COPY . .

# Should align with the ECS task definition
HEALTHCHECK --interval=30s --timeout=5s --retries=3 --start-period=60s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uv", "run", "fastapi", "run"]