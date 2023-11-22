#!/bin/sh

echo "Sharing ports for spark services..."
pid1=$(kubectl port-forward svc/minio 9001:9001 -n spark &)
pid3=$(kubectl port-forward svc/spark-history-node 18080:18080 &)


trap "kill -2 $pid1 $pid2 $pid3" SIGINT

echo "Closed ports for kafka."
