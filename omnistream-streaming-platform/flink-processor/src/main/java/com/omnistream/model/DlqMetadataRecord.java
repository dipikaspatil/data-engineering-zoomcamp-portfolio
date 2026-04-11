package com.omnistream.model;

import java.io.Serializable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DlqMetadataRecord implements Serializable {
    private static final long serialVersionUID = 1L;

    private String dlqId;
    private String sourceTopic;
    private String recordType;
    private String errorStage;
    private String errorType;
    private String errorClassification;
    private String status;
    private Integer retryCount;
    private Integer maxRetries;
    private Long nextRetryAt;
    private Long failedAt;
    private Long lastRetriedAt;
    private String payloadGcsPath;
    private String idempotencyKey;
}