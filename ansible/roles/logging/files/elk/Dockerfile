FROM sebp/elk:611

ENV ES_HOME /opt/elasticsearch
WORKDIR ${ES_HOME}

RUN CONF_DIR=/etc/elasticsearch gosu elasticsearch bin/elasticsearch-plugin \
    install ingest-user-agent

RUN CONF_DIR=/etc/elasticsearch gosu elasticsearch bin/elasticsearch-plugin \
    install ingest-geoip
