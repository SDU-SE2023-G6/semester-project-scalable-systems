#!/bin/sh

# this script can be executed only after streams are created

# TWEETS sink config
curl -X POST http://127.0.0.1:8083/connectors -H 'Content-Type: application/json' -d '{ "name": "hdfs-sink-tweets", "config": { "connector.class": "io.confluent.connect.hdfs.HdfsSinkConnector", "tasks.max": "5", "topics": " TWEET_AVRO", "hdfs.url": "hdfs://simple-hdfs-namenode-default-0.hadoop:8020", "flush.size": "3", "format.class": "io.confluent.connect.hdfs.avro.AvroFormat", "key.converter.schemas.enable":"false", "key.converter": "org.apache.kafka.connect.storage.StringConverter", "key.converter.schema.registry.url": "http://kafka-schema-registry.kafka:8081", "value.converter.schemas.enable":"false", "value.converter.schema.registry.url": "http://kafka-schema-registry.kafka:8081", "value.converter": "io.confluent.connect.avro.AvroConverter", "schemas.enable": "false" }}'

# BTC sink config
curl -X POST http://127.0.0.1:8083/connectors -H 'Content-Type: application/json' -d '{ "name": "hdfs-sink-btc", "config": { "connector.class": "io.confluent.connect.hdfs.HdfsSinkConnector", "tasks.max": "5", "topics": " BTC_PARQUET", "hdfs.url": "hdfs://simple-hdfs-namenode-default-0.hadoop:8020", "flush.size": "3", "format.class": "io.confluent.connect.hdfs.parquet.ParquetFormat", "key.converter.schemas.enable":"false", "key.converter": "org.apache.kafka.connect.storage.StringConverter", "key.converter.schema.registry.url": "http://kafka-schema-registry.kafka:8081", "value.converter.schemas.enable":"false", "value.converter.schema.registry.url": "http://kafka-schema-registry.kafka:8081", "value.converter": "io.confluent.connect.avro.AvroConverter", "schemas.enable": "false" }}'