FROM phusion/baseimage:latest

# install PostgreSQL
#RUN touch /etc/apt/sources.list.d/pgdg.list
#RUN echo "deb http://apt.postgresql.org/pub/repos/apt/ utopic-pgdg main" > /etc/apt/sources.list.d/pgdg.list
#RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
#apt-key add - && apt-get update
# RUN dpkg -i /tmp/postgresql-9.3.10-2-x64-bigsql.deb

RUN apt-get update
RUN apt-get install -y postgresql postgresql-contrib

RUN mkdir /home/postgres/
RUN chown -R postgres /home/postgres/
RUN chmod u+rX /home/postgres/


EXPOSE 5432
