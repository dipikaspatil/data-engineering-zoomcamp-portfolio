/**
 * This class is the internal representation of finance data. 
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
public class FinanceRecord implements Serializable {
    private String record_key;
    private String symbol;
    private Double price;
    private Long volume;
    private Long timestamp;
    private String change_percent;
}