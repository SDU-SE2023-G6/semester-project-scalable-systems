#!/bin/sh

# Preconditions
# - Namespace called stackable
# - Namespace called hadoop
# - Helm repo https://repo.stackable.tech/repository/helm-stable/ added

# Install Hive and Trino operator in stackable namespace
helm install --wait hive-operator stackable-stable/hive-operator --version 23.11.0 \
  --set resources.requests.cpu=5m \
  --set resources.requests.memory=50Mi \
  -n stackable
helm install --wait trino-operator stackable-stable/trino-operator --version 23.11.0 \
  --set resources.requests.cpu=5m \
  --set resources.requests.memory=50Mi \
  -n stackable

# Deploy PostgreSQL database to be used as Hive metastore in hadoop namespace
helm install postgresql \
--version=12.1.5 \
--namespace hadoop \
--set auth.username=hive \
--set auth.password=hive \
--set auth.database=hive \
--set primary.extendedConfiguration="password_encryption=md5" \
--repo https://charts.bitnami.com/bitnami postgresql

# Create Hive Metastore in hadoop namespace
kubectl apply -f hive.yaml -n hadoop

# Create Trino cluster, catalog and Hive connector in hadoop namespace
kubectl apply -f trino.yaml -n hadoop