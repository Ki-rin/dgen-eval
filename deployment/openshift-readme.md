# Deploying to OpenShift

This guide explains how to deploy the Documentation Evaluation Dashboard as a service on OpenShift.

## Prerequisites

- OpenShift CLI (`oc`) installed and configured
- Docker or Podman installed
- Access to an OpenShift cluster
- Container registry access

## Deployment Files

The project includes several files for OpenShift deployment:

1. `Dockerfile` - Container image definition
2. `openshift-deployment.yaml` - Deployment, Service, and Route configuration
3. `persistent-volumes.yaml` - Persistent Volume Claims for application data
4. `deploy-to-openshift.sh` - Deployment automation script
5. `healthcheck.py` - Health check endpoint for container monitoring

## Deployment Options

### Option 1: Using the Deployment Script

The simplest way to deploy is using the provided script:

```bash
# Make the script executable
chmod +x deploy-to-openshift.sh

# Run with default settings
./deploy-to-openshift.sh

# Or specify custom settings
./deploy-to-openshift.sh \
  --project-name my-doc-evaluator \
  --image-repo registry.example.com \
  --image-tag v1.0.0 \
  --storage-class managed-nfs-storage
```

### Option 2: Manual Deployment

If you prefer to deploy manually:

1. **Build the container image**:
   ```bash
   docker build -t registry.example.com/doc-evaluator-dashboard:latest .
   docker push registry.example.com/doc-evaluator-dashboard:latest
   ```

2. **Create OpenShift project**:
   ```bash
   oc new-project doc-evaluator
   ```

3. **Create persistent volume claims**:
   ```bash
   # Edit persistent-volumes.yaml first to set your storage class
   oc apply -f persistent-volumes.yaml
   ```

4. **Deploy the application**:
   ```bash
   # Edit openshift-deployment.yaml first to set your image repository
   oc apply -f openshift-deployment.yaml
   ```

5. **Verify deployment**:
   ```bash
   oc get pods
   oc get routes
   ```

## Configuration

### Environment Variables

The application uses the following environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| STREAMLIT_SERVER_PORT | 8080 | Port for Streamlit application |
| STREAMLIT_SERVER_HEADLESS | true | Run in headless mode |
| STREAMLIT_SERVER_ENABLE_CORS | false | CORS setting |
| STREAMLIT_SERVER_ADDRESS | 0.0.0.0 | Interface to bind to |
| HEALTH_CHECK_PORT | 8081 | Port for health checks |

### Persistent Storage

The deployment uses three Persistent Volume Claims:

1. `doc-evaluator-config-pvc` - For configuration files
2. `doc-evaluator-examples-pvc` - For example documents
3. `doc-evaluator-results-pvc` - For evaluation results

Adjust storage sizes in `persistent-volumes.yaml` based on your needs.

## Health Monitoring

The application includes a health check endpoint that:

1. Listens on port 8081 (configurable via HEALTH_CHECK_PORT)
2. Responds to GET requests at `/health`
3. Returns status 200 when the Streamlit application is healthy
4. Returns status 503 when the Streamlit application is unavailable

## Updating the Application

To update the application:

1. Build and push a new container image
2. Update the deployment:
   ```bash
   oc set image deployment/doc-evaluator-dashboard doc-evaluator-dashboard=registry.example.com/doc-evaluator-dashboard:new-tag
   ```

## Scaling

The application is designed to work with multiple replicas for high availability:

```bash
# Scale to 3 replicas
oc scale deployment doc-evaluator-dashboard --replicas=3
```

Note that when scaling, all replicas will share the same persistent volumes, so the application should be designed to handle concurrent access.

## Troubleshooting

- **Image Pull Issues**: Check your image repository access and credentials
- **Storage Issues**: Verify PVC status with `oc get pvc`
- **Application Errors**: Check logs with `oc logs deployment/doc-evaluator-dashboard`
- **Route Issues**: Verify route with `oc get route doc-evaluator-dashboard`
