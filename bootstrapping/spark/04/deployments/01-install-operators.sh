#!/bin/sh

kubectl create namespace stackable

helm install -n stackable commons-operator stackable-stable/commons-operator --version 23.7.0
helm install -n stackable secret-operator stackable-stable/secret-operator --version 23.7.0
helm install -n stackable spark-k8s-operator stackable-stable/spark-k8s-operator --version 23.7.0
