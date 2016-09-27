FROM ubuntu:trusty

# dummy Database data generator script
RUN mkdir /scripts/
ADD generator_script.py /scripts/
RUN chmod +x /scripts/generator_script.py

RUN apt-get update
RUN apt-get install -y nano wget aptitude ack-grep

RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ utopic-pgdg main" > /etc/apt/sources.list.d/pgdg.
RUN wget -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update
RUN aptitude install -f -y postgresql-common
RUN apt-get install -y postgresql-9.3 postgresql-contrib-9.3

RUN export PATH=$PATH:/usr/lib/postgresql/9.3/bin

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  trust" >> /etc/postgresql/9.3/main/pg_hba.conf

# create folder for PostgreSQL logs
RUN mkdir /pg_log
RUN chmod 777 /pg_log

# add custom config file including logging
ADD postgresql.conf /etc/postgresql/9.3/main/postgresql.conf

RUN /etc/init.d/postgresql restart

EXPOSE 5432
