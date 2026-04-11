/**
 * This class is the internal representation of geo data. 
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
public class GeoRecord implements Serializable {
    private String record_key;
    private String id;
    private Double mag;
    private String place;
    private Long timestamp;
    private Double lon;
    private Double lat;
    private Double depth;
}