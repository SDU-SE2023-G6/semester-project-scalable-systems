#!/bin/sh

helm install minio oci://registry-1.docker.io/bitnamicharts/minio --set service.type=NodePort --set defaultBuckets=spark-logs --set auth.rootUser=admin --set auth.rootPassword=password
