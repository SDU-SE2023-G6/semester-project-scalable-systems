#!/bin/sh

kubectl create namespace spark
kubectl create namespace stackable

# Install operators
helm install -n stackable commons-operator stackable-stable/commons-operator --version 23.7.0
helm install -n stackable --set kubeletDir=/var/snap/microk8s/common/var/lib/kubelet secret-operator stackable-stable/secret-operator --version 23.7.0
helm install -n stackable spark-k8s-operator stackable-stable/spark-k8s-operator --version 23.7.0

# Install chart
helm install -n spark minio oci://registry-1.docker.io/bitnamicharts/minio --set service.type=NodePort --set defaultBuckets=spark-logs --set auth.rootUser=admin --set auth.rootPassword=password

kubectl apply -n spark -f spark-configurations.yaml

kubectl apply -n spark -f spark-history-server.yaml
