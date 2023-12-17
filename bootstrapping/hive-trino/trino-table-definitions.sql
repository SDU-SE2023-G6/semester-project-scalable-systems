CREATE SCHEMA IF NOT EXISTS hive.btc
WITH (location = 'hdfs://simple-hdfs-namenode-default-0:8020/topics/');

CREATE TABLE IF NOT EXISTS hive.btc.tweet (
  id bigint,
  user varchar,
  fullname varchar,
  url varchar,
  timestamp bigint,
  replies integer,
  likes integer,
  retweets integer,
  text varchar
)
WITH (
   format = 'AVRO',
   external_location = 'hdfs://simple-hdfs-namenode-default-0:8020/topics/TWEET_AVRO/partition=0/'
);

CREATE TABLE IF NOT EXISTS hive.btc.bitcoin (
  timestamp bigint,
  open double,
  high double,
  low double,
  close double,
  volume_btc double,
  volume_currency double,
  weighted_price double
)
WITH (
   format = 'PARQUET',
   external_location = 'hdfs://simple-hdfs-namenode-default-0:8020/topics/BITCOIN_PARQUET/partition=0'
);