/**
 * This class is the internal representation of flight data. 
 * It must match the keys in Python Producer's JSON.
 */
package com.omnistream.model;

import java.io.Serializable;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class FlightRecord implements Serializable { // Serializable for BigQuery Sink.
    // Matches the keys from your Python Producer
    private String record_key;
    private String icao24;
    private String callsign;
    private String origin_country;
    private Long timestamp;      // 64-bit
    private Double latitude;     // 64-bit
    private Double longitude;    // 64-bit
    private Double velocity;     // 64-bit
}