package com.omnistream.model;

import java.io.Serializable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DlqRecord implements Serializable {
    private static final long serialVersionUID = 1L;

    private String dlqId;
    private String sourceTopic;
    private String recordType;

    // Where it failed
    private String errorStage;           // PARSE, CLASSIFY, VALIDATE, ENRICH, SINK
    private String errorType;            // PARSE_ERROR, VALIDATION_ERROR, UNKNOWN_TYPE, etc.
    private String errorReason;
    private String errorClassification;  // TRANSIENT, PERMANENT, MANUAL_REVIEW

    // Data
    private String rawPayload;
    private String payloadGcsPath;       // optional, filled later if needed
    private String idempotencyKey;

    // Retry control
    private Integer retryCount;
    private Integer maxRetries;
    private Long nextRetryAt;
    private String status;               // NEW, RETRYABLE, MANUAL_REVIEW, FAILED_PERMANENT, RESOLVED

    // Audit
    private Long failedAt;
    private Long lastRetriedAt;
}