#!/usr/bin/env bash
# Deploy Boombox frontend to Cloud Run.
# Usage: bash deploy/cloud-run-frontend.sh

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID}"
REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="boombox-frontend"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
BACKEND_URL="${BOOMBOX_BACKEND_URL:?Set BOOMBOX_BACKEND_URL to the backend Cloud Run URL}"

echo "→ Building frontend image..."
gcloud builds submit frontend/ \
  --tag "${IMAGE}" \
  --project "${PROJECT_ID}"

echo "→ Deploying to Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --allow-unauthenticated \
  --set-env-vars "NEXT_PUBLIC_BACKEND_URL=${BACKEND_URL}" \
  --min-instances 0 \
  --max-instances 5 \
  --memory 256Mi \
  --cpu 1

echo "✓ Frontend deployed."
gcloud run services describe "${SERVICE_NAME}" \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --format "value(status.url)"
