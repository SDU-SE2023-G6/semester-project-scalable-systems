#!/bin/sh

kubectl port-forward svc/redpanda  8080:8080 -n kafka & \
kubectl port-forward svc/kafka-schema-registry  8081:8081 -n kafka & \
kubectl port-forward svc/kafka-connect  8083:8083 -n kafka & \
kubectl port-forward svc/strimzi-kafka-bootstrap 9091:9091 -n kafka & \
kubectl port-forward svc/strimzi-kafka-bootstrap 9092:9092 -n kafka & \
kubectl port-forward svc/strimzi-kafka-bootstrap 9093:9093 -n kafka & \
kubectl port-forward deployment/grafana 3000:3000 -n kafka & \

echo "ctrl+\ or ctrl+break to stop the port-fowarding of kafka services.."
