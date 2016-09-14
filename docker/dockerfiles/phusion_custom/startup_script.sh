#!/bin/sh
/etc/init.d/postgresql restart
container_ip=$(awk 'END{print $1}' /etc/hosts)
psql -h $container_ip -U postgres -d postgres --command "ALTER USER \"postgres\" WITH PASSWORD 'postgres';"

# run dummy database creator cript
/scripts/generator_script.py -d $container_ip -u postgres -p postgres -t 5 -c 10 -r 20 -m
