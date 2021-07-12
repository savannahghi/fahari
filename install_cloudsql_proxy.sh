#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export CLOUD_SQL_PROXY_VERSION=v1.23.0

wget https://storage.googleapis.com/cloudsql-proxy/$CLOUD_SQL_PROXY_VERSION/cloud_sql_proxy.linux.amd64 -O /cloud_sql_proxy
chmod +x /cloud_sql_proxy

echo "Installed CloudSQL Proxy, version $CLOUD_SQL_PROXY_VERSION..."
