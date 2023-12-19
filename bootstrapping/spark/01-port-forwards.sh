#!/bin/sh

echo "Sharing ports for spark services..."
kubectl port-forward svc/minio 9001:9001 -n spark &
kubectl port-forward svc/spark-history-node 18080:18080 &