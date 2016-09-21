#!/bin/sh
while true
do
	echo "TEST BEGIN"
	free && sync && echo 3 > /proc/sys/vm/drop_caches && free
	docker exec postgres_test service postgresql restart &
	java -cp "/home/mkamras/Eclipses/EE_Luna/workspace/postgres.dbclient/target/postgres.dbclient-0.0.1-SNAPSHOT.jar:/usr/share/java/postgresql-jdbc4-9.2.jar:/home/mkamras/.m2/repository/org/apache/commons/commons-csv/1.4/commons-csv-1.4.jar" postgres.dbclient.DBClient /home/mkamras/psgre_test/phusion/gen/csv/ ; exitCode=$?
	if [ "$exitCode" -eq "1" ]
	then
		echo "Inconsistent state found."
	else
		echo "No problems detected."
	fi
	echo "TEST END"
done
