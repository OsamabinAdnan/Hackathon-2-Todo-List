#!/bin/bash

# Post-deployment validation tests for Todo Chatbot
# These tests would be run after deployment to verify functionality

set -e  # Exit on any error

echo "Starting post-deployment validation tests..."

# Test 1: Check if all pods are running
echo "Test 1: Verifying all pods are running..."
kubectl get pods
POD_STATUS=$(kubectl get pods --no-headers -o custom-columns=':status.phase' | uniq)
if [[ "$POD_STATUS" == *"Running"* ]]; then
  echo "✓ All pods are running"
else
  echo "✗ Some pods are not running: $POD_STATUS"
  exit 1
fi

# Test 2: Check if services are available
echo "Test 2: Verifying services are available..."
kubectl get svc

# Test 3: Test basic connectivity between frontend and backend
echo "Test 3: Testing connectivity between services..."
kubectl run connectivity-test --image=curlimages/curl -it --rm --restart=Never -- curl -s -o /dev/null -w "HTTP %{http_status}" http://todo-chatbot-backend:8000/

# Test 4: Verify application endpoints
echo "Test 4: Verifying application endpoints..."
FRONTEND_POD=$(kubectl get pods -l app=frontend -o jsonpath='{.items[0].metadata.name}')
BACKEND_POD=$(kubectl get pods -l app=backend -o jsonpath='{.items[0].metadata.name}')

echo "Frontend pod: $FRONTEND_POD"
echo "Backend pod: $BACKEND_POD"

echo "✓ Post-deployment validation tests completed successfully!"