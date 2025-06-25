# Kafka, Spark, ELK, and Monitoring Stack with Docker Compose

This project sets up a full-featured data streaming and monitoring environment using Docker Compose. It includes a multi-broker, multi-controller Apache Kafka cluster (KRaft mode), Spark, Schema Registry, Redpanda Console, Java producer, Prometheus, Alertmanager, Grafana, Elasticsearch, Kibana, Filebeat, and Logstash.

## Features
- **Kafka (KRaft mode):** Multi-controller, multi-broker, no Zookeeper
- **Spark:** Distributed data processing
- **Schema Registry:** Avro schema management
- **Redpanda Console:** Kafka UI
- **Java Producer:** Example Kafka producer
- **Prometheus & Alertmanager:** Metrics collection and alerting
- **Grafana:** Pre-provisioned dashboards for Kafka and Spark
- **Elasticsearch, Kibana, Filebeat, Logstash:** Centralized log collection, parsing, and visualization

## Services Overview
- **Kafka Controllers/Brokers:** High-availability, JMX exporter for metrics
- **Spark Master/Workers:** For distributed computation
- **Schema Registry:** For Avro schemas
- **Redpanda Console:** Kafka topic and schema UI
- **Java Producer:** Example app (see `Main.java`)
- **Prometheus:** Scrapes metrics from Kafka, Spark, etc.
- **Alertmanager:** Handles Prometheus alerts
- **Grafana:** Dashboards for metrics
- **Elasticsearch:** Log storage
- **Kibana:** Log search and visualization
- **Filebeat:** Ships logs to Elasticsearch or Logstash
- **Logstash:** (Optional) Log parsing/filtering before Elasticsearch

## Quick Start
1. **Clone the repo:**
   ```sh
   git clone <this-repo>
   cd <this-repo>
   ```
2. **Build and start all services:**
   ```sh
   docker-compose up --build
   ```
3. **Access UIs:**
   - Kafka brokers: `localhost:29092`, `39092`, `49092`
   - Redpanda Console: [http://localhost:8080](http://localhost:8080)
   - Schema Registry: [http://localhost:18081](http://localhost:18081)
   - Spark Master: [http://localhost:9190](http://localhost:9190)
   - Prometheus: [http://localhost:9090](http://localhost:9090)
   - Grafana: [http://localhost:3000](http://localhost:3000) (default: admin/admin)
   - Elasticsearch: [http://localhost:9200](http://localhost:9200)
   - Kibana: [http://localhost:5601](http://localhost:5601)

## Log Collection & Monitoring
- **Kafka and Spark logs** are collected by Filebeat and optionally processed by Logstash before being indexed in Elasticsearch.
- **Metrics** are scraped by Prometheus and visualized in Grafana (see pre-provisioned dashboards).
- **Alertmanager** handles alert rules defined in `monitoring/prometheus/rules/alert_rules.yml`.

## Configuration
- **Kafka JMX Exporter:** Config in `volumes/jmx_exporter/kafka-broker.yml`
- **Prometheus:** Config in `monitoring/prometheus/prometheus.yml`
- **Grafana Dashboards:** Provisioned in `monitoring/grafana/provisioning/dashboards/`
- **Filebeat:** Config in `monitoring/elk/filebeat/filebeat.yml`
- **Logstash:** Pipeline config in `monitoring/elk/logstash/pipeline/`

## Troubleshooting
- If Filebeat fails to start, check file permissions and log file paths in `filebeat.yml`.
- If Grafana shows no data, check Prometheus targets and metric names.
- If Elasticsearch OOMs, adjust JVM heap size in the `elasticsearch` service.
- For log visibility in Kibana, ensure index pattern matches `kafka-logs-filebeat-*`.

