FROM phusion/baseimage:latest

# add our script that runs at startup of container
ADD startup_script.sh /etc/my_init.d/

# make it executable
RUN chmod +x /etc/my_init.d/startup_script.sh

# dummy Database data generator script
RUN mkdir /scripts/
ADD generator_script.py /scripts/
RUN chmod +x /scripts/generator_script.py

# enable SSH
RUN rm -f /etc/service/sshd/down

# Regenerate SSH host keys. baseimage-docker does not contain any, so you
# have to do that yourself. You may also comment out this instruction; the
# init system will auto-generate one during boot.
RUN /etc/my_init.d/00_regen_ssh_host_keys.sh
RUN /usr/sbin/enable_insecure_key

EXPOSE 22

# utils
RUN apt-get update
RUN apt-get install -y nano wget

# allow installation of postgresql-9.3
RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ utopic-pgdg main" > /etc/apt/sources.list.d/pgdg.list
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update
RUN apt-get install -y postgresql-9.3 postgresql-contrib-9.3
RUN export PATH=$PATH:/usr/lib/postgresql/9.3/bin

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  trust" >> /etc/postgresql/9.3/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/9.3/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/9.3/main/postgresql.conf

RUN /etc/init.d/postgresql restart

EXPOSE 5432

# USER postgres

# Add VOLUMEs to allow backup of config, logs and databases
# VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
