#!/bin/bash
# =============================================================================
# PrimerLab Genomic - Container Builder Script
# v1.2.0 - Local automation for Docker and Singularity builds
# =============================================================================

set -e

# Base directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "============================================="
echo "🧬 PrimerLab Genomic Container Builder"
echo "============================================="

# 1. Docker Build
echo -e "\n[1/2] Building Docker Image..."
if command -v docker &> /dev/null; then
    docker build -t primerlab:latest -t primerlab:1.2.0 .
    echo "✅ Docker image 'primerlab:latest' successfully built."
else
    echo "⚠️ Docker is not installed or running. Skipping Docker build."
fi

# 2. Singularity / Apptainer Build
echo -e "\n[2/2] Building Singularity Image..."
if command -v singularity &> /dev/null; then
    singularity build primerlab.sif Singularity.def
    echo "✅ Singularity SIF image 'primerlab.sif' successfully built."
elif command -v apptainer &> /dev/null; then
    apptainer build primerlab.sif Singularity.def
    echo "✅ Apptainer SIF image 'primerlab.sif' successfully built."
else
    echo "⚠️ Singularity or Apptainer is not installed. Skipping SIF build."
    echo "   You can build it on an HPC cluster using:"
    echo "   singularity build primerlab.sif Singularity.def"
fi

echo -e "\n============================================="
echo "🎉 Container build process finished!"
echo "============================================="
