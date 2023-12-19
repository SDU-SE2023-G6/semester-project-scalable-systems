#!/bin/sh

helm repo add stackable-stable https://repo.stackable.tech/repository/helm-stable/

helm install --wait commons-operator stackable-stable/commons-operator --version 23.11.0
helm install --wait secret-operator stackable-stable/secret-operator --version 23.11.0
helm install --wait listener-operator stackable-stable/listener-operator --version 23.11.0
helm install --wait zookeeper-operator stackable-stable/zookeeper-operator --version 23.11.0
helm install --wait hdfs-operator stackable-stable/hdfs-operator --version 23.11.0
helm install --wait druid-operator stackable-stable/druid-operator --version 23.11.0
