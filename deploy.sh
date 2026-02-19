#!/bin/bash

# Configuration variables
PROJECT_ID="molten-album-478703-d8"
REGION="us-central1"
SERVICE_NAME="dashboard-agent"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
SERVICE_ACCOUNT="dashboard-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Starting deployment to GCP Cloud Run with Vertex AI..."
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo ""

# 1. Set the active project
echo "📋 Setting GCP project..."
gcloud config set project ${PROJECT_ID}

# 2. Enable required APIs
echo "🔌 Enabling required GCP APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage-api.googleapis.com

# 3. Create service account if it doesn't exist
echo "👤 Setting up service account..."
if ! gcloud iam service-accounts describe ${SERVICE_ACCOUNT} &>/dev/null; then
    echo "Creating service account..."
    gcloud iam service-accounts create dashboard-agent-sa \
        --display-name="Dashboard Agent Service Account" \
        --description="Service account for Dashboard Agent application"
else
    echo "Service account already exists"
fi

# 4. Grant necessary permissions
echo "🔐 Granting IAM permissions..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/aiplatform.user" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.objectViewer" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/logging.logWriter" \
    --condition=None

# 5. Build the Docker image
echo "🏗️  Building Docker image..."
cd backend
gcloud builds submit --tag ${IMAGE_NAME}
cd ..

# 6. Deploy to Cloud Run
echo "🚢 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --service-account ${SERVICE_ACCOUNT} \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID},GCP_LOCATION=${REGION}" \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 80

# 7. Get the service URL
echo ""
echo "📍 Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --region ${REGION} \
  --format 'value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Service URL: ${SERVICE_URL}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next steps:"
echo "1. Test the deployment:"
echo "   curl ${SERVICE_URL}/health"
echo ""
echo "2. Update your frontend .env file:"
echo "   VITE_API_URL=${SERVICE_URL}"
