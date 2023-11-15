#!/bin/sh

# File for bootstraping a kafka producer. If you want to delete these resources then just delete the kafka namespace.


kubectl create namespace kafka

helm install -n kafka strimzi-cluster-operator oci://quay.io/strimzi-helm/strimzi-kafka-operator --set watchAnyNamespace=true

kubectl get pod -n kafka --watch

kubectl apply -n kafka -f kafka.yaml

kubectl wait kafka/strimzi --for=condition=Ready --timeout=300s -n kafka

kubectl apply -n kafka -f kafka-extra.yaml

