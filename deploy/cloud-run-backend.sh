#!/usr/bin/env bash
# Deploy Boombox backend to Cloud Run.
# Usage: bash deploy/cloud-run-backend.sh

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="boombox-backend"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "→ Building backend image..."
gcloud builds submit backend/ \
  --tag "${IMAGE}" \
  --project "${PROJECT_ID}"

echo "→ Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --allow-unauthenticated \
  --set-env-vars "BOOMBOX_MOCK=false" \
  --min-instances 0 \
  --max-instances 5 \
  --memory 512Mi \
  --cpu 1

echo "✓ Backend deployed."
gcloud run services describe "${SERVICE_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format "value(status.url)"
