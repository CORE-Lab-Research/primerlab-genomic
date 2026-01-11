# =============================================================================
# PrimerLab Genomic - Multi-stage Dockerfile
# v0.9.0 - Cross-platform container with all dependencies
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies and build wheel
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (for cache efficiency)
COPY pyproject.toml README.md ./
COPY primerlab/ ./primerlab/

# Build wheel
RUN pip install --no-cache-dir build && \
    python -m build --wheel

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Slim production image
# -----------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

LABEL maintainer="Engki Nandatama <engkinandatama@outlook.com>"
LABEL description="PrimerLab Genomic - Automated Primer and Probe Design"
LABEL version="0.9.0"

WORKDIR /app

# Install system dependencies for bioinformatics tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    # ViennaRNA for secondary structure prediction
    vienna-rna \
    # BLAST+ for off-target detection
    ncbi-blast+ \
    # Utilities
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy wheel from builder and install
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm -rf /tmp/*.whl

# Copy example configs (optional, for user convenience)
COPY examples/ /app/examples/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash primerlab
USER primerlab

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PRIMERLAB_HOME=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD primerlab --version || exit 1

# Default command - show help
ENTRYPOINT ["primerlab"]
CMD ["--help"]

# =============================================================================
# Usage:
#   docker build -t primerlab .
#   docker run primerlab --version
#   docker run -v $(pwd):/data primerlab run pcr --config /data/config.yaml
# =============================================================================
