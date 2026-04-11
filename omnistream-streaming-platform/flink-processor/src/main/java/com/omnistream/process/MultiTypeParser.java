package com.omnistream.process;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.omnistream.model.DlqRecord;
import com.omnistream.model.FinanceRecord;
import com.omnistream.model.FlightRecord;
import com.omnistream.model.GeoRecord;

import org.apache.flink.streaming.api.functions.ProcessFunction;
import org.apache.flink.util.Collector;
import org.apache.flink.util.OutputTag;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.UUID;

public class MultiTypeParser extends ProcessFunction<String, Void> {

    private static final long serialVersionUID = 1L;

    private transient ObjectMapper objectMapper;

    public static final OutputTag<GeoRecord> GEO_TAG =
            new OutputTag<GeoRecord>("geo-tag") {};

    public static final OutputTag<DlqRecord> DLQ_TAG =
            new OutputTag<DlqRecord>("dlq-tag") {};

    public static final OutputTag<FlightRecord> AVIATION_TAG =
        new OutputTag<FlightRecord>("aviation-tag") {};

    public static final OutputTag<FinanceRecord> FINANCE_TAG =
            new OutputTag<FinanceRecord>("finance-tag") {};

    @Override
    public void processElement(String rawJson, Context ctx, Collector<Void> out) {
        if (objectMapper == null) {
            objectMapper = new ObjectMapper();
        }

        try {
            JsonNode root = objectMapper.readTree(rawJson);

            String sourceTopic = getText(root, "sourceTopic");
            JsonNode payload = root.get("payload");

            if (!notBlank(sourceTopic) || payload == null || payload.isNull()) {
                ctx.output(DLQ_TAG, buildDlqRecord(
                        "unknown",
                        "unknown",
                        "PARSE",
                        "PARSE_ERROR",
                        "Missing sourceTopic or payload",
                        rawJson
                ));
                return;
            }

            if (isGeo(payload)) {
                GeoRecord geo = parseGeo(payload);
                if (isValidGeo(geo)) {
                    ctx.output(GEO_TAG, geo);
                } else {
                    ctx.output(DLQ_TAG, buildDlqRecord(
                            sourceTopic, "geo", "VALIDATE", "VALIDATION_ERROR",
                            buildGeoValidationError(geo), payload.toString()));
                }
                return;
            }

            if (isFinance(payload)) {
                FinanceRecord finance = parseFinance(payload);
                if (isValidFinance(finance)) {
                    ctx.output(FINANCE_TAG, finance);
                } else {
                    ctx.output(DLQ_TAG, buildDlqRecord(
                            sourceTopic, "finance", "VALIDATE", "VALIDATION_ERROR",
                            buildFinanceValidationError(finance), payload.toString()));
                }
                return;
            }

            if (isAviation(payload)) {
                FlightRecord aviation = parseAviation(payload);
                if (isValidAviation(aviation)) {
                    ctx.output(AVIATION_TAG, aviation);
                } else {
                    ctx.output(DLQ_TAG, buildDlqRecord(
                            sourceTopic, "aviation", "VALIDATE", "VALIDATION_ERROR",
                            buildAviationValidationError(aviation), payload.toString()));
                }
                return;
            }

            ctx.output(DLQ_TAG, buildDlqRecord(
                    sourceTopic,
                    "unknown",
                    "CLASSIFY",
                    "UNKNOWN_TYPE",
                    "Unable to classify message",
                    payload.toString()
            ));
        } catch (Exception e) {
            ctx.output(DLQ_TAG, buildDlqRecord(
                    "unknown",
                    "unknown",
                    "PARSE",
                    "PARSE_ERROR",
                    e.getMessage(),
                    rawJson
            ));
        }
    }

    private boolean isGeo(JsonNode root) {
        return root.has("id")
                && root.has("mag")
                && root.has("place")
                && root.has("timestamp")
                && root.has("lon")
                && root.has("lat")
                && root.has("depth");
    }

    private boolean isFinance(JsonNode root) {
        return root.has("symbol")
                && root.has("price")
                && root.has("timestamp");
    }

    private boolean isAviation(JsonNode root) {
        return root.has("icao24")
                && root.has("timestamp");
    }

    private GeoRecord parseGeo(JsonNode root) {
        GeoRecord record = new GeoRecord();
        
        record.setId(getText(root, "id"));
        record.setMag(getDouble(root, "mag"));
        record.setPlace(getText(root, "place"));
        record.setTimestamp(getLong(root, "timestamp"));
        record.setLon(getDouble(root, "lon"));
        record.setLat(getDouble(root, "lat"));
        record.setDepth(getDouble(root, "depth"));
        record.setRecord_key(buildIdempotencyKey("geo", "geo", root.toString()));

        return record;
    }

    private FinanceRecord parseFinance(JsonNode root) {
        FinanceRecord record = new FinanceRecord();

        record.setSymbol(getText(root, "symbol"));
        record.setPrice(getDouble(root, "price"));
        record.setVolume(getLong(root, "volume"));
        record.setTimestamp(getLong(root, "timestamp"));
        record.setChange_percent(getText(root, "change_percent"));
        record.setRecord_key(buildIdempotencyKey("finance", "finance", root.toString()));

        return record;
    }

    private FlightRecord parseAviation(JsonNode root) {
        FlightRecord record = new FlightRecord();

        record.setIcao24(getText(root, "icao24"));
        record.setCallsign(getText(root, "callsign"));
        record.setOrigin_country(getText(root, "origin_country"));
        record.setTimestamp(getLong(root, "timestamp"));
        record.setLatitude(getDouble(root, "latitude"));
        record.setLongitude(getDouble(root, "longitude"));
        record.setVelocity(getDouble(root, "velocity"));
        record.setRecord_key(buildIdempotencyKey("aviation", "aviation", root.toString()));

        return record;
    }

    private boolean isValidGeo(GeoRecord r) {
        return r != null
                && notBlank(r.getId())
                && r.getTimestamp() != null
                && r.getMag() != null
                && r.getDepth() != null
                && r.getLat() != null && r.getLat() >= -90 && r.getLat() <= 90
                && r.getLon() != null && r.getLon() >= -180 && r.getLon() <= 180;
    }

    private boolean isValidFinance(FinanceRecord r) {
        return r != null
                && notBlank(r.getSymbol())
                && r.getPrice() != null && r.getPrice() > 0
                && r.getTimestamp() != null;
    }

    private boolean isValidAviation(FlightRecord r) {
        return r != null
                && notBlank(r.getIcao24())
                && r.getTimestamp() != null
                && (r.getLatitude() == null || (r.getLatitude() >= -90 && r.getLatitude() <= 90))
                && (r.getLongitude() == null || (r.getLongitude() >= -180 && r.getLongitude() <= 180));
    }

    private String buildGeoValidationError(GeoRecord r) {
        if (r == null) return "Geo record is null";
        if (!notBlank(r.getId())) return "Missing or blank id";
        if (r.getTimestamp() == null) return "Missing timestamp";
        if (r.getMag() == null) return "Missing mag";
        if (r.getDepth() == null) return "Missing depth";
        if (r.getLat() == null) return "Missing lat";
        if (r.getLon() == null) return "Missing lon";
        if (r.getLat() < -90 || r.getLat() > 90) return "Latitude out of range";
        if (r.getLon() < -180 || r.getLon() > 180) return "Longitude out of range";
        return "Unknown geo validation error";
    }

    private String buildFinanceValidationError(FinanceRecord r) {
        if (r == null) return "Finance record is null";
        if (!notBlank(r.getSymbol())) return "Missing symbol";
        if (r.getPrice() == null) return "Missing price";
        if (r.getPrice() <= 0) return "Invalid price";
        if (r.getTimestamp() == null) return "Missing timestamp";
        if (r.getVolume() != null && r.getVolume() < 0) return "Invalid volume";
        return "Unknown finance validation error";
    }

    private String buildAviationValidationError(FlightRecord r) {
        if (r == null) return "Aviation record is null";
        if (!notBlank(r.getIcao24())) return "Missing or blank icao24";
        if (r.getTimestamp() == null) return "Missing timestamp";
        if (r.getLatitude() != null && (r.getLatitude() < -90 || r.getLatitude() > 90)) return "Latitude out of range";
        if (r.getLongitude() != null && (r.getLongitude() < -180 || r.getLongitude() > 180)) return "Longitude out of range";
        if (r.getVelocity() != null && r.getVelocity() < 0) return "Velocity cannot be negative";
        //if (!notBlank(r.getCallsign())) return "Missing or blank callsign";
        //if (!notBlank(r.getOrigin_country())) return "Missing or blank origin_country";
        return "Unknown aviation validation error";
    }

    private DlqRecord buildDlqRecord(
            String sourceTopic,
            String recordType,
            String errorStage,
            String errorType,
            String errorReason,
            String rawPayload
    ) {
        String classification = classifyError(errorType);
        String status = initialStatus(classification);
        long now = System.currentTimeMillis();

        return new DlqRecord(
                UUID.randomUUID().toString(),                  // dlqId
                sourceTopic,
                recordType,
                errorStage,
                errorType,
                errorReason,
                classification,
                rawPayload,
                null,                                          // payloadGcsPath
                buildIdempotencyKey(sourceTopic, recordType, rawPayload),
                0,                                             // retryCount
                2,                                             // maxRetries
                classification.equals("TRANSIENT") ? now + 15 * 60 * 1000 : null,
                status,
                now,
                null
        );
    }

    private String classifyError(String errorType) {
        switch (errorType) {
            case "SINK_TIMEOUT":
            case "BQ_TEMP_FAILURE":
            case "NETWORK_ERROR":
            case "RATE_LIMIT":
                return "TRANSIENT";
            case "UNKNOWN_TYPE":
                return "MANUAL_REVIEW";
            case "PARSE_ERROR":
            case "VALIDATION_ERROR":
            default:
                return "PERMANENT";
        }
    }

    private String initialStatus(String classification) {
        switch (classification) {
            case "TRANSIENT":
                return "RETRYABLE";
            case "MANUAL_REVIEW":
                return "MANUAL_REVIEW";
            default:
                return "FAILED_PERMANENT";
        }
    }

    private String buildIdempotencyKey(String sourceTopic, String recordType, String rawPayload) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            String input = sourceTopic + "|" + recordType + "|" + rawPayload;
            byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
            StringBuilder sb = new StringBuilder();
            for (byte b : hash) {
                sb.append(String.format("%02x", b));
            }
            return sb.toString();
        } catch (Exception e) {
            return UUID.randomUUID().toString();
        }
    }


    private String getText(JsonNode node, String field) {
        JsonNode value = node.get(field);
        return (value == null || value.isNull()) ? null : value.asText();
    }

    private Double getDouble(JsonNode node, String field) {
        JsonNode value = node.get(field);
        return (value == null || value.isNull()) ? null : value.asDouble();
    }

    private Long getLong(JsonNode node, String field) {
        JsonNode value = node.get(field);
        return (value == null || value.isNull()) ? null : value.asLong();
    }

    private boolean notBlank(String s) {
        return s != null && !s.trim().isEmpty();
    }
}