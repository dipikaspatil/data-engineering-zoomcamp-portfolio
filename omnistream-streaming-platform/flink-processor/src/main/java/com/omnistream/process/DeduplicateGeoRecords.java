package com.omnistream.process;

import com.omnistream.model.GeoRecord;
import org.apache.flink.api.common.state.ValueState;
import org.apache.flink.api.common.state.ValueStateDescriptor;
import org.apache.flink.api.common.state.StateTtlConfig;
import org.apache.flink.api.common.time.Time;
import org.apache.flink.configuration.Configuration;
import org.apache.flink.streaming.api.functions.KeyedProcessFunction;
import org.apache.flink.util.Collector;

public class DeduplicateGeoRecords extends KeyedProcessFunction<String, GeoRecord, GeoRecord> {

    private transient ValueState<Boolean> seenState;

    @Override
    public void open(Configuration parameters) {
        StateTtlConfig ttlConfig = StateTtlConfig
                .newBuilder(Time.days(1))
                .setUpdateType(StateTtlConfig.UpdateType.OnCreateAndWrite)
                .build();

        ValueStateDescriptor<Boolean> descriptor =
                new ValueStateDescriptor<>("seen-geo-record", Boolean.class);

        descriptor.enableTimeToLive(ttlConfig);
        seenState = getRuntimeContext().getState(descriptor);
    }

    @Override
    public void processElement(GeoRecord value, Context ctx, Collector<GeoRecord> out) throws Exception {
        Boolean seen = seenState.value();
        if (seen == null || !seen) {
            seenState.update(true);
            out.collect(value);
        }
    }
}