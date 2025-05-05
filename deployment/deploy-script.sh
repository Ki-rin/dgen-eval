#!/bin/bash
# Script to deploy the documentation evaluation dashboard to OpenShift

set -e

# Configuration - modify these variables for your environment
PROJECT_NAME="doc-evaluator"
IMAGE_REPOSITORY="your-registry.example.com"
IMAGE_NAME="doc-evaluator-dashboard"
IMAGE_TAG="latest"
STORAGE_CLASS_NAME="standard"  # Adjust based on your OpenShift cluster's available storage classes

# Function to display usage information
show_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --project-name NAME       OpenShift project name (default: $PROJECT_NAME)"
    echo "  --image-repo REPO         Container image repository (default: $IMAGE_REPOSITORY)"
    echo "  --image-tag TAG           Container image tag (default: $IMAGE_TAG)"
    echo "  --storage-class NAME      Storage class name (default: $STORAGE_CLASS_NAME)"
    echo "  --help                    Display this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --project-name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --image-repo)
            IMAGE_REPOSITORY="$2"
            shift 2
            ;;
        --image-tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --storage-class)
            STORAGE_CLASS_NAME="$2"
            shift 2
            ;;
        --help)
            show_usage
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
done

# Check if oc CLI is installed
if ! command -v oc &> /dev/null; then
    echo "Error: OpenShift CLI (oc) is not installed or not in PATH."
    echo "Please install the OpenShift CLI before running this script."
    exit 1
fi

# Check if docker/podman is installed
if command -v docker &> /dev/null; then
    CONTAINER_CLI="docker"
elif command -v podman &> /dev/null; then
    CONTAINER_CLI="podman"
else
    echo "Error: Neither Docker nor Podman is installed or in PATH."
    echo "Please install a container CLI before running this script."
    exit 1
fi

echo "=========================="
echo "Deployment Configuration:"
echo "=========================="
echo "Project name:    $PROJECT_NAME"
echo "Image repository: $IMAGE_REPOSITORY"
echo "Image tag:       $IMAGE_TAG"
echo "Storage class:   $STORAGE_CLASS_NAME"
echo "=========================="

# Prompt for confirmation
read -p "Proceed with deployment? (y/n): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Deployment aborted."
    exit 0
fi

# Create or switch to project
echo "Creating/switching to project '$PROJECT_NAME'..."
oc new-project $PROJECT_NAME 2>/dev/null || oc project $PROJECT_NAME

# Build container image
echo "Building container image..."
$CONTAINER_CLI build -t $IMAGE_REPOSITORY/$IMAGE_NAME:$IMAGE_TAG .

# Push container image to registry
echo "Pushing image to registry..."
$CONTAINER_CLI push $IMAGE_REPOSITORY/$IMAGE_NAME:$IMAGE_TAG

# Create persistent volume claims
echo "Creating persistent volume claims..."
cat persistent-volumes.yaml | \
    sed "s|\${STORAGE_CLASS_NAME}|$STORAGE_CLASS_NAME|g" | \
    oc apply -f -

# Deploy application
echo "Deploying application..."
cat openshift-deployment.yaml | \
    sed "s|\${IMAGE_REPOSITORY}|$IMAGE_REPOSITORY|g" | \
    oc apply -f -

# Wait for deployment to become ready
echo "Waiting for deployment to become ready..."
oc rollout status deployment/doc-evaluator-dashboard --timeout=300s

# Get route information
ROUTE_HOST=$(oc get route doc-evaluator-dashboard -o jsonpath='{.spec.host}')

echo "=========================="
echo "Deployment Successful!"
echo "=========================="
echo "The Documentation Evaluation Dashboard is available at:"
echo "https://$ROUTE_HOST"
echo "=========================="
