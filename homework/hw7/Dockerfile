FROM flink:1.19.0-scala_2.12

# Install Python 3, pip, and the JDK development headers
USER root

# 1. Install system dependencies + OpenJDK 11 headers
RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev openjdk-11-jdk-headless && \
    rm -rf /var/lib/apt/lists/*

# 2. AUTOMATION: Create the symlink so 'python' points to 'python3'
RUN ln -s /usr/bin/python3 /usr/bin/python

# 3. Point to the newly installed OpenJDK 11
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-arm64
# Note: If you are on an Intel Mac, use: /usr/lib/jvm/java-11-openjdk-amd64
# But since you are 'niteshmishra@Mac', arm64 is likely correct.

# 4. Create a symbolic link to the path pemja is obsessed with
RUN mkdir -p /opt/java && \
    ln -s $JAVA_HOME /opt/java/openjdk

# 5. Install Python dependencies for Flink and Postgres connectivity
RUN pip3 install --no-cache-dir \
    apache-flink==1.19.0 \
    psycopg2-binary

# 6. Download Flink Connectors (Automated)
# We use the 3.3.0-1.19 versions which are specifically built for Flink 1.19
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-kafka/3.3.0-1.19/flink-sql-connector-kafka-3.3.0-1.19.jar && \
    wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-jdbc/3.2.0-1.19/flink-connector-jdbc-3.2.0-1.19.jar && \
    wget -P /opt/flink/lib/ https://jdbc.postgresql.org/download/postgresql-42.7.5.jar