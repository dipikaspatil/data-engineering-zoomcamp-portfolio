/**
 * Omnistream Medallion Pipeline
 * This Flink job reads from multiple Kafka topics, performs basic validation, and writes to both Kafka (Silver) and BigQuery (Gold).
 * Key Features:
 * - Unified Kafka Source: Reads from all three raw topics in one stream.
 * - Basic Validation: Filters out records that don't contain expected identifiers.
 * - Silver Sink: Writes sanitized JSON back to Kafka for downstream processing.
 * - Gold Sink: Writes structured data to BigQuery with exactly-once semantics.
 * - Checkpointing: Configured for exactly-once processing with appropriate timeouts and intervals
 * - Side Outputs: Uses Flink's side outputs to route different data types to their respective sinks.
 * Note: This is a simplified example for demonstration purposes. In production, you'd likely want more robust error handling, schema validation, and dynamic topic/table management.
 * 
 */
package com.omnistream;

import com.omnistream.model.DlqMetadataRecord;
import com.omnistream.model.DlqRecord;
import com.omnistream.model.FinanceRecord;
import com.omnistream.model.FlightRecord;
import com.omnistream.model.GeoRecord;
import com.omnistream.process.DeduplicateGeoRecords;
import com.omnistream.process.MultiTypeParser;
import com.omnistream.model.InboundEvent;

import org.apache.avro.generic.GenericRecord;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.connector.kafka.sink.KafkaRecordSerializationSchema;
import org.apache.flink.connector.kafka.sink.KafkaSink;
import org.apache.flink.connector.kafka.source.KafkaSource;
import org.apache.flink.connector.kafka.source.enumerator.initializer.OffsetsInitializer;
import org.apache.flink.formats.avro.typeutils.GenericRecordAvroTypeInfo;
import org.apache.flink.streaming.api.CheckpointingMode;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.datastream.SingleOutputStreamOperator;
import org.apache.flink.streaming.api.environment.CheckpointConfig.ExternalizedCheckpointCleanup;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.kafka.clients.admin.AdminClient;
import org.apache.kafka.clients.admin.AdminClientConfig;
import org.apache.kafka.clients.admin.NewTopic;
import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;

import java.util.List;
import java.util.ArrayList;
import java.util.Map;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Properties;
import java.util.Set;
import java.util.regex.Pattern;
import java.util.concurrent.TimeUnit;
import java.io.IOException;

import org.apache.flink.api.common.serialization.SerializationSchema;
import com.google.cloud.flink.bigquery.sink.BigQuerySink;
import com.google.cloud.flink.bigquery.sink.BigQuerySinkConfig;
import com.google.cloud.flink.bigquery.sink.serializer.AvroToProtoSerializer;
import org.apache.flink.connector.base.DeliveryGuarantee;
import com.omnistream.process.DeduplicateFinanceRecords;
import com.omnistream.process.DeduplicateAviationRecords;

import org.apache.flink.connector.file.sink.FileSink;
import org.apache.flink.core.fs.Path;
import org.apache.flink.api.common.serialization.SimpleStringEncoder;
import org.apache.flink.streaming.api.functions.sink.filesystem.rollingpolicies.DefaultRollingPolicy;
import org.apache.flink.configuration.MemorySize;

import org.apache.flink.streaming.api.functions.sink.filesystem.BucketAssigner;
import org.apache.flink.streaming.api.functions.sink.filesystem.bucketassigners.SimpleVersionedStringSerializer;
import org.apache.flink.core.io.SimpleVersionedSerializer;
import org.apache.flink.api.common.serialization.SimpleStringSchema;

import java.time.Duration;


public class StreamingJob {
        private static final String AVIATION_SCHEMA_JSON =
                "{\n" +
                "  \"type\": \"record\",\n" +
                "  \"name\": \"AviationRecord\",\n" +
                "  \"namespace\": \"com.omnistream.avro\",\n" +
                "  \"fields\": [\n" +
                "    {\"name\": \"record_key\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"icao24\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"callsign\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"origin_country\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"timestamp\", \"type\": [\"null\", \"long\"], \"default\": null},\n" +
                "    {\"name\": \"latitude\", \"type\": [\"null\", \"double\"], \"default\": null},\n" +
                "    {\"name\": \"longitude\", \"type\": [\"null\", \"double\"], \"default\": null},\n" +
                "    {\"name\": \"velocity\", \"type\": [\"null\", \"double\"], \"default\": null}\n" +
                "  ]\n" +
                "}";

        private static final Schema AVIATION_AVRO_SCHEMA = new Schema.Parser().parse(AVIATION_SCHEMA_JSON); 
        
        private static final String FINANCE_SCHEMA_JSON =
                "{\n" +
                "  \"type\": \"record\",\n" +
                "  \"name\": \"FinanceRecord\",\n" +
                "  \"namespace\": \"com.omnistream.avro\",\n" +
                "  \"fields\": [\n" +
                "    {\"name\": \"record_key\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"symbol\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"price\", \"type\": [\"null\", \"double\"], \"default\": null},\n" +
                "    {\"name\": \"volume\", \"type\": [\"null\", \"long\"], \"default\": null},\n" +
                "    {\"name\": \"timestamp\", \"type\": [\"null\", \"long\"], \"default\": null},\n" +
                "    {\"name\": \"change_percent\", \"type\": [\"null\", \"string\"], \"default\": null}\n" +
                "  ]\n" +
                "}";
        
        private static final Schema FINANCE_AVRO_SCHEMA = new Schema.Parser().parse(FINANCE_SCHEMA_JSON);

        private static final String GEO_SCHEMA_JSON =
                "{\n" +
                "  \"type\": \"record\",\n" +
                "  \"name\": \"GeoRecord\",\n" +
                "  \"namespace\": \"com.omnistream.avro\",\n" +
                "  \"fields\": [\n" +
                "    {\"name\": \"record_key\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"id\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"mag\", \"type\": [\"null\", \"double\"], \"default\": null},\n" +
                "    {\"name\": \"place\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"timestamp\", \"type\": [\"null\", \"long\"], \"default\": null},\n" +
                "    {\"name\": \"lon\", \"type\": [\"null\", \"double\"], \"default\": null},\n" +
                "    {\"name\": \"lat\", \"type\": [\"null\", \"double\"], \"default\": null},\n" +
                "    {\"name\": \"depth\", \"type\": [\"null\", \"double\"], \"default\": null}\n" +
                "  ]\n" +
                "}";
        
        private static final Schema GEO_AVRO_SCHEMA = new Schema.Parser().parse(GEO_SCHEMA_JSON);

        private static final String DLQ_METADATA_SCHEMA_JSON =
                "{\n" +
                "  \"type\": \"record\",\n" +
                "  \"name\": \"DlqMetadataRecord\",\n" +
                "  \"namespace\": \"com.omnistream.avro\",\n" +
                "  \"fields\": [\n" +
                "    {\"name\": \"dlqId\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"sourceTopic\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"recordType\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"errorStage\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"errorType\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"errorClassification\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"status\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"retryCount\", \"type\": [\"null\", \"int\"], \"default\": null},\n" +
                "    {\"name\": \"maxRetries\", \"type\": [\"null\", \"int\"], \"default\": null},\n" +
                "    {\"name\": \"nextRetryAt\", \"type\": [\"null\", \"long\"], \"default\": null},\n" +
                "    {\"name\": \"failedAt\", \"type\": [\"null\", \"long\"], \"default\": null},\n" +
                "    {\"name\": \"lastRetriedAt\", \"type\": [\"null\", \"long\"], \"default\": null},\n" +
                "    {\"name\": \"payloadGcsPath\", \"type\": [\"null\", \"string\"], \"default\": null},\n" +
                "    {\"name\": \"idempotencyKey\", \"type\": [\"null\", \"string\"], \"default\": null}\n" +
                "  ]\n" +
                "}";

        private static final Schema DLQ_METADATA_AVRO_SCHEMA =
                new Schema.Parser().parse(DLQ_METADATA_SCHEMA_JSON);

    public static void main(String[] args) throws Exception {
                // Logic to bridge .env variable to the Google SDK
                String gcpKeyPath = System.getenv("GCP_KEY_PATH");
                if (gcpKeyPath != null) {
                        System.setProperty("GOOGLE_APPLICATION_CREDENTIALS", gcpKeyPath);
                }

                String bootstrapServers = System.getenv("KAFKA_BOOTSTRAP_SERVERS_INTERNAL");
                if (bootstrapServers == null)
                        bootstrapServers = "redpanda:9092";

                // 4. BIGQUERY SINKS
                String projectId = System.getenv("GCP_PROJECT_ID");
                if(projectId == null) {
                        projectId = "de-zoomcamp-2026-486900"; // Default for local testing
                }

                String dataset = System.getenv("BQ_STG_DATASET");
                if(dataset == null) {
                        dataset = "omnistream_staging"; // Default for local testing
                }

                ensureTopicsExist(bootstrapServers);

                // 1. ENVIRONMENT SETUP
                final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

                System.out.println("Dipika Starting Omnistream Medallion Pipeline with bootstrap servers: "
                                + bootstrapServers);

                // Checkpointing Strategy for 3 Sinks
                env.enableCheckpointing(60000);
                env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
                env.getCheckpointConfig().setMinPauseBetweenCheckpoints(30000);
                env.getCheckpointConfig().setCheckpointTimeout(300000);
                env.getCheckpointConfig().setMaxConcurrentCheckpoints(1);
                env.getCheckpointConfig()
                                .setExternalizedCheckpointCleanup(ExternalizedCheckpointCleanup.RETAIN_ON_CANCELLATION);
                env.setParallelism(1);

                String archiveBucket = System.getenv("GCS_COLD_ARCHIVE_BUCKET");
                if (archiveBucket == null) {
                        archiveBucket = "de-zoomcamp-2026-486900-raw-archive";
                }
                String archiveBasePath = "gs://" + archiveBucket;

                String errorLakeBucket = System.getenv("GCS_ERROR_LAKE_BUCKET");
                if (errorLakeBucket == null) {
                        errorLakeBucket = projectId + "-error-lake";
                }
                String errorLakeBasePath = "gs://" + errorLakeBucket + "/";

                // 2. UNIFIED SOURCE (Step 3: API -> Redpanda)
                KafkaSource<String> multiSource = KafkaSource.<String>builder()
                        .setBootstrapServers(bootstrapServers)
                        .setTopicPattern(Pattern.compile("(raw|retry)_.*"))
                        .setGroupId("omnistream-multi-consumer-7")
                        .setStartingOffsets(OffsetsInitializer.earliest())
                        .setValueOnlyDeserializer(new SimpleStringSchema())
                        .build();

                System.out.println("Subscribed to Kafka topics matching pattern: (raw|retry)_.*");

                DataStream<String> rawStream = env.fromSource(
                        multiSource,
                        WatermarkStrategy.noWatermarks(),
                        "Unified Source"
                );

                System.out.println("Created unified Kafka source stream. Now processing...");

                // 3. MULTI-TYPE PARSER (Step 4: Branching/Validation)
                SingleOutputStreamOperator<Void> branchedStream = rawStream.process(new MultiTypeParser());

                System.out.println("Completed parsing and branching. Now writing to sinks...");
                DataStream<FlightRecord> processedAviationStream = branchedStream.getSideOutput(MultiTypeParser.AVIATION_TAG);
                DataStream<GeoRecord> processedGeoStream = branchedStream.getSideOutput(MultiTypeParser.GEO_TAG);
                DataStream<FinanceRecord> processedFinanceStream = branchedStream.getSideOutput(MultiTypeParser.FINANCE_TAG);
                

                // Send validated records to Kafka (Silver) topics - these are the "processed_" topics that downstream consumers can subscribe to for further enrichment or analysis.
                System.out.println("Writing to processed Kafka sinks: processed_geo_data, processed_finance_data, processed_aviation_data");
                processedGeoStream.sinkTo(buildKafkaSink(bootstrapServers, "processed_geo_data")).name("GeoProcessedKafkaSink");
                processedFinanceStream.sinkTo(buildKafkaSink(bootstrapServers, "processed_finance_data")).name("FinanceProcessedKafkaSink");
                processedAviationStream.sinkTo(buildKafkaSink(bootstrapServers, "processed_aviation_data")).name("AviationProcessedKafkaSink");

                // For BigQuery, we want to ensure we only write unique records based on their natural keys to avoid duplicates in the Gold layer.
                System.out.println("Deduplicating records for BigQuery sinks...");
                DataStream<GeoRecord> uniqueGeoForBqStream = processedGeoStream.keyBy(GeoRecord::getRecord_key).process(new DeduplicateGeoRecords());
                DataStream<FinanceRecord> uniqueFinanceForBqStream = processedFinanceStream.keyBy(FinanceRecord::getRecord_key).process(new DeduplicateFinanceRecords());
                DataStream<FlightRecord> uniqueAviationForBqStream = processedAviationStream.keyBy(FlightRecord::getRecord_key).process(new DeduplicateAviationRecords()); // icao24 + "_" + timestamp + "_" + latitude + "_" + longitude - Later we may need ot change

                System.out.println("Writing deduplicated processed records to GCS cold archive...");
                uniqueGeoForBqStream
                        .map(record -> OBJECT_MAPPER.writeValueAsString(record))
                        .sinkTo(buildGcsArchiveSink(archiveBasePath + "/source_type=geo"))
                        .name("GeoGcsArchiveSink");

                uniqueFinanceForBqStream
                        .map(record -> OBJECT_MAPPER.writeValueAsString(record))
                        .sinkTo(buildGcsArchiveSink(archiveBasePath + "/source_type=finance"))
                        .name("FinanceGcsArchiveSink");

                uniqueAviationForBqStream
                        .map(record -> OBJECT_MAPPER.writeValueAsString(record))
                        .sinkTo(buildGcsArchiveSink(archiveBasePath + "/source_type=aviation"))
                        .name("AviationGcsArchiveSink");


                System.out.println("Writing to BigQuery Gold sink: raw_aviation_data, raw_finance_data, raw_geo_data");
                uniqueAviationForBqStream
                        .map(StreamingJob::toAviationGenericRecord)
                        .returns(new GenericRecordAvroTypeInfo(AVIATION_AVRO_SCHEMA))
                        .sinkTo(buildBqSink(env, projectId, dataset, "raw_aviation_data"))
                        .name("AviationBigQuerySink");

                uniqueFinanceForBqStream
                        .map(StreamingJob::toFinanceGenericRecord)
                        .returns(new GenericRecordAvroTypeInfo(FINANCE_AVRO_SCHEMA))
                        .sinkTo(buildBqSink(env, projectId, dataset, "raw_finance_data"))
                        .name("FinanceBigQuerySink");

                uniqueGeoForBqStream
                        .map(StreamingJob::toGeoGenericRecord)
                        .returns(new GenericRecordAvroTypeInfo(GEO_AVRO_SCHEMA))
                        .sinkTo(buildBqSink(env, projectId, dataset, "raw_geo_data"))
                        .name("GeoBigQuerySink");

                // Handle DLQ records: Write the raw payload to GCS for later analysis and write metadata to BigQuery for monitoring and alerting.
                DataStream<DlqRecord> rawDlqStream = branchedStream.getSideOutput(MultiTypeParser.DLQ_TAG);

                DataStream<DlqRecord> dlqStream = rawDlqStream.map(record -> {
                java.time.Instant instant = java.time.Instant.ofEpochMilli(record.getFailedAt());
                java.time.ZonedDateTime zdt = instant.atZone(java.time.ZoneOffset.UTC);

                String hourPartition = String.format(
                        "%04d-%02d-%02d--%02d",
                        zdt.getYear(),
                        zdt.getMonthValue(),
                        zdt.getDayOfMonth(),
                        zdt.getHour()
                );

                String stage = record.getErrorStage() == null
                        ? "unknown"
                        : record.getErrorStage().toLowerCase();

               String payloadPath = String.format(
                        "%serror_stage=%s/%s/dlq_id=%s/",
                        errorLakeBasePath,
                        stage,
                        hourPartition,
                        record.getDlqId()
                );

                record.setPayloadGcsPath(payloadPath);
                return record;
                }).name("DlqPathEnrichment");

                DataStream<DlqMetadataRecord> dlqMetadataStream = dlqStream.map(record -> new DlqMetadataRecord(
                record.getDlqId(),
                record.getSourceTopic(),
                record.getRecordType(),
                record.getErrorStage(),
                record.getErrorType(),
                record.getErrorClassification(),
                record.getStatus(),
                record.getRetryCount(),
                record.getMaxRetries(),
                record.getNextRetryAt(),
                record.getFailedAt(),
                record.getLastRetriedAt(),
                record.getPayloadGcsPath(),
                record.getIdempotencyKey()
                )).name("DlqMetadataMapping");

                // Send invalid records to DLQ Kafka topic
                System.out.println("Writing to DLQ Kafka sink: dead_letter_queue");                
                dlqStream.sinkTo(buildKafkaSink(bootstrapServers, "dead_letter_queue")).name("DlqKafkaSink");

                System.out.println("Writing DLQ records to GCS Error Lake...");
                // That is the minimal version. Better version later: partition by error_stage and record_type.
                dlqStream
                        .sinkTo(buildDlqErrorLakeSink(errorLakeBasePath))
                        .name("DlqGcsErrorLakeSink");

                System.out.println("Writing DLQ metadata to BigQuery...");
                dlqMetadataStream
                .map(StreamingJob::toDlqMetadataGenericRecord)
                .returns(new GenericRecordAvroTypeInfo(DLQ_METADATA_AVRO_SCHEMA))
                .sinkTo(buildBqSink(env, projectId, dataset, "dlq_control"))
                .name("DlqMetadataBigQuerySink");

                env.execute("Omnistream Medallion Pipeline");
        }

        /**
         * Simplified Helper to build BigQuery Sinks for Map data.
         * This version is "Universal" for Aviation, Geo, and Finance.
        */
        private static org.apache.flink.api.connector.sink2.Sink<GenericRecord> buildBqSink(
                        StreamExecutionEnvironment env,
                        String project,
                        String dataset,
                        String table) throws IOException {

                // 1. Setup Options
                com.google.cloud.flink.bigquery.common.config.BigQueryConnectOptions options = com.google.cloud.flink.bigquery.common.config.BigQueryConnectOptions
                                .builder()
                                .setProjectId(project)
                                .setDataset(dataset)
                                .setTable(table)
                                .build();

                // 2. Setup Config using the built-in RowSerializer for Maps
                BigQuerySinkConfig<GenericRecord> sinkConfig =
                        BigQuerySinkConfig.<GenericRecord>newBuilder()
                                .connectOptions(options)
                                .streamExecutionEnvironment(env)
                                .deliveryGuarantee(DeliveryGuarantee.AT_LEAST_ONCE)
                                .serializer(new AvroToProtoSerializer()
                        )
                        .build();

                // 3. Return the Sink
                return com.google.cloud.flink.bigquery.sink.BigQuerySink.get(sinkConfig);
        }

        private static final com.fasterxml.jackson.databind.ObjectMapper OBJECT_MAPPER =
                new com.fasterxml.jackson.databind.ObjectMapper();

        private static <T> KafkaSink<T> buildKafkaSink(String bootstrapServers, String topic) {
                return KafkaSink.<T>builder()
                        .setBootstrapServers(bootstrapServers)
                        .setRecordSerializer(
                                KafkaRecordSerializationSchema.<T>builder()
                                        .setTopic(topic)
                                        .setValueSerializationSchema(new JsonSerializationSchema<T>())
                                        .build()
                        )
                        .build();
        }

        private static class JsonSerializationSchema<T> implements SerializationSchema<T> {
        @Override
        public byte[] serialize(T element) {
                try {
                return OBJECT_MAPPER.writeValueAsBytes(element);
                } catch (Exception e) {
                throw new RuntimeException("Failed to serialize to JSON", e);
                }
        }
        }

        private static GenericRecord toAviationGenericRecord(FlightRecord record) {
                GenericRecord avro = new GenericData.Record(AVIATION_AVRO_SCHEMA);
        
                avro.put("record_key", record.getRecord_key());
                avro.put("icao24", record.getIcao24());
                avro.put("callsign", record.getCallsign());
                avro.put("origin_country", record.getOrigin_country());
                avro.put("timestamp", record.getTimestamp());
                avro.put("latitude", record.getLatitude());
                avro.put("longitude", record.getLongitude());
                avro.put("velocity", record.getVelocity());

                System.out.println("Dipika AVIATION AVRO DEBUG -> "
                        + "record_key=" + record.getRecord_key()
                        + ", icao24=" + record.getIcao24()
                        + ", callsign=" + record.getCallsign()
                        + ", origin_country=" + record.getOrigin_country()
                        + ", timestamp=" + record.getTimestamp()
                        + ", latitude=" + record.getLatitude()
                        + ", longitude=" + record.getLongitude()
                        + ", velocity=" + record.getVelocity());

                System.out.println("Dipika AVIATION GENERIC RECORD -> " + avro);

                return avro;
        }

        // Mapper for FinanceRecord to GenericRecord using the defined Avro schema
        private static GenericRecord toFinanceGenericRecord(FinanceRecord record) {
                GenericRecord avro = new GenericData.Record(FINANCE_AVRO_SCHEMA);

                avro.put("record_key", record.getRecord_key());
                avro.put("symbol", record.getSymbol());
                avro.put("price", record.getPrice());
                avro.put("volume", record.getVolume());
                avro.put("timestamp", record.getTimestamp());
                avro.put("change_percent", record.getChange_percent());

                System.out.println("Dipika FINANCE AVRO DEBUG -> "
                        + "record_key=" + record.getRecord_key()
                        + ", symbol=" + record.getSymbol()
                        + ", price=" + record.getPrice()
                        + ", volume=" + record.getVolume()
                        + ", timestamp=" + record.getTimestamp()
                        + ", change_percent=" + record.getChange_percent());

                System.out.println("Dipika FINANCE GENERIC RECORD -> " + avro);

                return avro;
        }

        // Mapper for GeoRecord to GenericRecord using the defined Avro schema
        private static GenericRecord toGeoGenericRecord(com.omnistream.model.GeoRecord record) {
                GenericRecord avro = new GenericData.Record(GEO_AVRO_SCHEMA); 

                avro.put("record_key", record.getRecord_key());
                avro.put("id", record.getId());
                avro.put("mag", record.getMag());
                avro.put("place", record.getPlace());
                avro.put("timestamp", record.getTimestamp());
                avro.put("lon", record.getLon());
                avro.put("lat", record.getLat());
                avro.put("depth", record.getDepth()); 

                System.out.println("Dipika GEO AVRO DEBUG -> "
                        + "record_key=" + record.getRecord_key()
                        + ", id=" + record.getId()
                        + ", mag=" + record.getMag()
                        + ", place=" + record.getPlace()
                        + ", timestamp=" + record.getTimestamp()
                        + ", lon=" + record.getLon()
                        + ", lat=" + record.getLat()
                        + ", depth=" + record.getDepth());

                System.out.println("Dipika GEO GENERIC RECORD -> " + avro);

                return avro;
        }

        // Mapper for DlqMetadataRecord to GenericRecord using the defined Avro schema
        private static GenericRecord toDlqMetadataGenericRecord(DlqMetadataRecord record) {
                GenericRecord avro = new GenericData.Record(DLQ_METADATA_AVRO_SCHEMA);

                avro.put("dlqId", record.getDlqId());
                avro.put("sourceTopic", record.getSourceTopic());
                avro.put("recordType", record.getRecordType());
                avro.put("errorStage", record.getErrorStage());
                avro.put("errorType", record.getErrorType());
                avro.put("errorClassification", record.getErrorClassification());
                avro.put("status", record.getStatus());
                avro.put("retryCount", record.getRetryCount());
                avro.put("maxRetries", record.getMaxRetries());
                avro.put("nextRetryAt", record.getNextRetryAt());
                avro.put("failedAt", record.getFailedAt());
                avro.put("lastRetriedAt", record.getLastRetriedAt());
                avro.put("payloadGcsPath", record.getPayloadGcsPath());
                avro.put("idempotencyKey", record.getIdempotencyKey());

                return avro;
        }

        private static void ensureTopicsExist(String bootstrapServers) {
                Properties props = new Properties();
                props.put(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);

                int rawPartitions = Integer.parseInt(
                        System.getenv().getOrDefault("KAFKA_RAW_PARTITIONS", "3")
                );

                int processedPartitions = Integer.parseInt(
                        System.getenv().getOrDefault("KAFKA_PROCESSED_PARTITIONS", "3")
                );

                int retryPartitions = Integer.parseInt(
                        System.getenv().getOrDefault("KAFKA_RETRY_PARTITIONS", "1")
                );

                int dlqPartitions = Integer.parseInt(
                        System.getenv().getOrDefault("KAFKA_DLQ_PARTITIONS", "1")
                );

                try (AdminClient admin = AdminClient.create(props)) {
                        Set<String> existingTopics = admin.listTopics().names().get(10, TimeUnit.SECONDS);
                        List<NewTopic> topicsToCreate = new ArrayList<>();
                        Map<String, Integer> topicPartitions = new LinkedHashMap<>();

                        topicPartitions.put("raw_geo_data", rawPartitions);
                        topicPartitions.put("raw_finance_data", rawPartitions);
                        topicPartitions.put("raw_aviation_data", rawPartitions);
                        topicPartitions.put("processed_geo_data", processedPartitions);
                        topicPartitions.put("processed_finance_data", processedPartitions);
                        topicPartitions.put("processed_aviation_data", processedPartitions);
                        topicPartitions.put("retry_geo_data", retryPartitions);
                        topicPartitions.put("retry_finance_data", retryPartitions);
                        topicPartitions.put("retry_aviation_data", retryPartitions);
                        topicPartitions.put("dead_letter_queue", dlqPartitions);

                        for (Map.Entry<String, Integer> entry : topicPartitions.entrySet()) {
                                addTopicIfMissing(existingTopics, topicsToCreate, entry.getKey(), entry.getValue(), (short) 1);
                        }

                        if (!topicsToCreate.isEmpty()) {
                                admin.createTopics(topicsToCreate).all().get(10, TimeUnit.SECONDS);

                                List<String> createdTopicNames = new ArrayList<>();
                                for (NewTopic topic : topicsToCreate) {
                                        createdTopicNames.add(topic.name());
                                }
                                System.out.println("Created missing topics: " + createdTopicNames);
                        } else {
                                System.out.println("All required topics already exist.");
                        }

                } catch (Exception e) {
                        throw new RuntimeException("Failed to ensure Kafka topics exist", e);
                }
                }

        private static void addTopicIfMissing(
                        Set<String> existingTopics,
                        List<NewTopic> topicsToCreate,
                        String topicName,
                        int partitions,
                        short replicationFactor
        ) {
                        if (!existingTopics.contains(topicName)) {
                                NewTopic topic = new NewTopic(topicName, partitions, replicationFactor);

                                Map<String, String> configs = new HashMap<>();
                                if ("dead_letter_queue".equals(topicName)) {
                                configs.put("retention.ms", "604800000"); // 7 days
                                } else {
                                configs.put("retention.ms", "259200000"); // 3 days
                                }

                                topic.configs(configs);
                                topicsToCreate.add(topic);

                                System.out.println("Topic '" + topicName + "' is missing and will be created.");
                        }
        }

        private static FileSink<String> buildGcsArchiveSink(String path) {
                return FileSink
                        .forRowFormat(
                                new Path(path),
                                new SimpleStringEncoder<String>("UTF-8")
                        )
                        /*
                                * Rolling policy configuration:
                                * - Rollover Interval: 1 minute (rolls over to a new file every minute)
                                * - Inactivity Interval: 30 seconds (if no new data arrives for 30 seconds, it rolls over to a new file)
                                * - Max Part Size: 8 MB (if a file exceeds 8 MB, it rolls over to a new file)
                                * This combination ensures that we get reasonably sized files in GCS without waiting too long, which is important for downstream processing and cost management in the cold archive.
                                * In a real production scenario, you might want to adjust these parameters based on the expected data volume and arrival patterns to optimize for both performance and cost. 
                                * For example, if you expect very high throughput, you might want to increase the max part size or decrease the rollover interval. 
                                * Conversely, for low throughput, you might want to increase the inactivity interval to avoid creating too many small files.
                                * 
                                * Prod Settings (example):
                                * inactivity: 5 min
                                * rollover: 15 min
                                * max size: 128 MiB
                         */
                        .withRollingPolicy(
                                DefaultRollingPolicy.builder()
                                        .withRolloverInterval(Duration.ofMinutes(1))
                                        .withInactivityInterval(Duration.ofSeconds(30))
                                        .withMaxPartSize(MemorySize.ofMebiBytes(8))
                                        .build()
                                )
                        .build();
        }

        /*
                1 record per file with file structure like:
                error_stage=classify/2026-04-01--10/dlq_id=2f339020.../part-0000   -> 1 record
                error_stage=parse/2026-04-01--10/dlq_id=6bab67bc.../part-0000      -> 1 record
        */
        private static FileSink<DlqRecord> buildDlqErrorLakeSink(String basePath) {
                return FileSink.<DlqRecord>forRowFormat(
                        new Path(basePath),
                        (element, stream) -> {
                                byte[] bytes = OBJECT_MAPPER.writeValueAsBytes(element);
                                stream.write(bytes);
                                stream.write('\n');
                        }
                )
                .withBucketAssigner(new BucketAssigner<DlqRecord, String>() {
                        @Override
                        public String getBucketId(DlqRecord element, Context context) {
                        java.time.Instant instant = java.time.Instant.ofEpochMilli(element.getFailedAt());
                        java.time.ZonedDateTime zdt = instant.atZone(java.time.ZoneOffset.UTC);

                        String hourPartition = String.format(
                                "%04d-%02d-%02d--%02d",
                                zdt.getYear(),
                                zdt.getMonthValue(),
                                zdt.getDayOfMonth(),
                                zdt.getHour()
                        );

                        String stage = element.getErrorStage() == null
                                ? "unknown"
                                : element.getErrorStage().toLowerCase();

                        return String.format(
                                "error_stage=%s/%s/dlq_id=%s",
                                stage,
                                hourPartition,
                                element.getDlqId()
                        );
                        }

                        @Override
                        public SimpleVersionedSerializer<String> getSerializer() {
                        return SimpleVersionedStringSerializer.INSTANCE;
                        }
                })
                .withRollingPolicy(
                        DefaultRollingPolicy.builder()
                                .withRolloverInterval(Duration.ofSeconds(1))
                                .withInactivityInterval(Duration.ofSeconds(1))
                                .withMaxPartSize(MemorySize.ofMebiBytes(1))
                                .build()
                )
                .build();
        }
}