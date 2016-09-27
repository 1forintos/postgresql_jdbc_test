#!/bin/sh
/etc/init.d/postgresql start
container_ip=$(awk 'END{print $1}' /etc/hosts)
psql -h $container_ip -U postgres -d postgres --command "ALTER USER \"postgres\" WITH PASSWORD 'postgres';"
