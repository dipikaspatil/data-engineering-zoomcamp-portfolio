FROM flink:1.19.0-scala_2.12

USER root

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev openjdk-11-jdk-headless wget && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
RUN mkdir -p /opt/java && \
    ln -s $JAVA_HOME /opt/java/openjdk

RUN pip3 install --no-cache-dir \
    apache-flink==1.19.0 \
    psycopg2-binary

# Optional connectors you already use
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.19/flink-sql-connector-kafka-3.3.0-1.19.jar && \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-jdbc/3.2.0-1.19/flink-connector-jdbc-3.2.0-1.19.jar && \
    wget -P /opt/flink/lib/ https://jdbc.postgresql.org/download/postgresql-42.7.5.jar

# Install the Flink GCS filesystem plugin in the correct plugins directory
RUN mkdir -p /opt/flink/plugins/flink-gs-fs-hadoop && \
    wget -O /opt/flink/plugins/flink-gs-fs-hadoop/flink-gs-fs-hadoop-1.19.1.jar \
      https://repo1.maven.org/maven2/org/apache/flink/flink-gs-fs-hadoop/1.19.1/flink-gs-fs-hadoop-1.19.1.jar