#!/bin/bash

# Step 1: Delete the existing Kind cluster to ensure a clean start
echo "Deleting existing Kind cluster..."
kind delete cluster

# Step 2: Create a new Kind cluster with the correct port mappings
echo "Creating new Kind cluster with port mappings..."
kind create cluster --config kind-config.yml

# Step 3: Install the NGINX Ingress controller
echo "Installing NGINX Ingress controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Step 4: Wait for the Ingress controller to be ready
echo "Waiting for Ingress controller to be ready..."
kubectl wait --namespace ingress-nginx \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/component=controller \
    --timeout=90s

# Step 5: Apply all application manifests in the correct order
echo "Applying all application manifests..."
kubectl apply -f namespace.yml
kubectl apply -f postgres-external-service.yml
kubectl apply -f app-deployment.yml
kubectl apply -f app-service.yml
kubectl apply -f ingress.yml

# Step 6: Verify the final state of all resources in your namespace
echo "Verifying all resources in the prod-contacts-app namespace..."
kubectl get all -n prod-contacts-app
