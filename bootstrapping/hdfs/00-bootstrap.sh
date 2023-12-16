#!/bin/sh

# Preconditions
# - Namespace called stackable
# - Namespace called hadoop
# - Helm repo https://repo.stackable.tech/repository/helm-stable/ added

# Install operators in stackable namespace
helm install --wait zookeeper-operator stackable-stable/zookeeper-operator --version 23.11.0 \
  -n stackable \
  --set resources.requests.cpu=5m \
  --set resources.requests.memory=50Mi
helm install --wait hdfs-operator stackable-stable/hdfs-operator --version 23.11.0 \
  -n stackable \
  --set resources.requests.cpu=5m \
  --set resources.requests.memory=50Mi
helm install --wait commons-operator stackable-stable/commons-operator --version 23.11.0 \
  -n stackable
helm install --wait listener-operator stackable-stable/listener-operator --version 23.11.0 \
  -n stackable
# Following line for running on MicroK8S
helm install --wait secret-operator stackable-stable/secret-operator --version 23.11.0 \
  --set kubeletDir=/var/snap/microk8s/common/var/lib/kubelet \
  -n stackable
# Following line for running on other than MicroK8S, e.g. locally w/ Docker Desktop or minikube
# helm install --wait secret-operator stackable-stable/secret-operator --version 23.11.0 -n hadoop

# Create resources in hadoop namespace
kubectl apply -f zk.yaml -n hadoop
kubectl apply -f znode.yaml -n hadoop
kubectl rollout status --watch --timeout=5m statefulset/simple-zk-server-default -n hadoop

kubectl apply -f hdfs.yaml -n hadoop
kubectl rollout status --watch --timeout=5m statefulset/simple-hdfs-datanode-default -n hadoop
kubectl rollout status --watch --timeout=5m statefulset/simple-hdfs-namenode-default -n hadoop
kubectl rollout status --watch --timeout=5m statefulset/simple-hdfs-journalnode-default -n hadoop

# Create interactive container to be able to access the HDFS files
kubectl run -n hadoop apache -i --tty --image apache/hadoop:3 --attach=false -- bash