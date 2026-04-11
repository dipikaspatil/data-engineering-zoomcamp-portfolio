package com.omnistream.model;

import java.io.Serializable;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class InboundEvent implements Serializable {
    private String sourceTopic;
    private String payload;
}