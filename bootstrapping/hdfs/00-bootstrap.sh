#!/bin/sh

#todo: description
#todo: test if it works

# Create namespace
kubectl create namespace hadoop

# Add stackable helm repo
helm repo add stackable-stable https://repo.stackable.tech/repository/helm-stable/ -n hadoop

# Install operators
helm install --wait zookeeper-operator stackable-stable/zookeeper-operator --version 23.11.0 -n hadoop
helm install --wait hdfs-operator stackable-stable/hdfs-operator --version 23.11.0 -n hadoop
helm install --wait commons-operator stackable-stable/commons-operator --version 23.11.0 -n hadoop
helm install --wait secret-operator stackable-stable/secret-operator --version 23.11.0 --set kubeletDir=/var/snap/microk8s/common/ -n hadoopvar/lib/kubelet
helm install --wait listener-operator stackable-stable/listener-operator --version 23.11.0 -n hadoop

# Apply resources
kubectl apply -f zk.yaml -n hadoop
kubectl apply -f znode.yaml -n hadoop
kubectl rollout status --watch --timeout=5m statefulset/simple-zk-server-default -n hadoop

kubectl apply -f hdfs.yaml -n hadoop
kubectl rollout status --watch --timeout=5m statefulset/simple-hdfs-datanode-default -n hadoop
kubectl rollout status --watch --timeout=5m statefulset/simple-hdfs-namenode-default -n hadoop
kubectl rollout status --watch --timeout=5m statefulset/simple-hdfs-journalnode-default -n hadoop

# Create interactive container to be able to access the HDFS files
kubectl run -n hadoop apache -i --tty --image apache/hadoop:3 --attach=false -- bash