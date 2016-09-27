#!/bin/sh
while true
do
	echo "TEST BEGIN"
	free && sync && echo 3 > /proc/sys/vm/drop_caches && free
	service postgresql stop
	nice -n 19 service postgresql start &
	nice -n -20 java -cp "jars/postgres.dbclient-0.0.1-SNAPSHOT.jar:jars/postgresql-jdbc4-9.2.jar:jars/commons-csv-1.4.jar" postgres.dbclient.DBClient csv/ 192.168.1.20 ; exitCode=$?
	if [ "$exitCode" -eq "1" ]
	then
		echo "Inconsistent state found."
		break
	fi
	echo "TEST END"
done

