#!/bin/sh

# Install stackable operators
helm repo add stackable-stable https://repo.stackable.tech/repository/helm-stable/
helm install -n hadoop commons-operator stackable-stable/commons-operator --version 23.7.0
helm install -n hadoop secret-operator stackable-stable/secret-operator --version 23.7.0 --set kubeletDir=/var/snap/microk8s/common/var/lib/kubelet
helm install -n hadoop hive-operator stackable-stable/hive-operator --version 23.7.0
helm install -n hadoop trino-operator stackable-stable/trino-operator --version 23.7.0

sleep 30

# Deploy PostgreSQL database to be used as Hive metastore 
helm install postgresql \
--version=12.1.5 \
--namespace hadoop \
--set auth.username=hive \
--set auth.password=hive \
--set auth.database=hive \
--set primary.extendedConfiguration="password_encryption=md5" \
--repo https://charts.bitnami.com/bitnami postgresql

sleep 30

# Create distributed, fault-tolerant data warehouse, i.e. Apache Hive
kubectl apply -f hive.yaml -n hadoop

sleep 30

# Create Trino cluster, catalog and connector to Hive
kubectl apply -f trino.yaml -n hadoop