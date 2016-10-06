#!/bin/bash
while true
do
	echo "TEST BEGIN"

	PQPING_OK=0
	ping_result=-1

	docker exec postgres_9.3.14 free && sync && free
	docker exec postgres_9.3.14 service postgresql stop
	docker exec postgres_9.3.14 service postgresql start &

	echo "PING.."
	while [ $ping_result != $PQPING_OK ]; do
		./testlibpq $2 ; ping_result=$?
	done
	echo "PING OK"

	java -cp "jars/postgres.dbclient.jar:jars/postgresql-jdbc4-9.2.jar:jars/commons-csv-1.4.jar" postgres.dbclient.DBClient gen/csv/ $1 ; exitCode=$?
	if [ "$exitCode" -eq "1" ]
	then
		echo "Records dont match."
		break
	fi

	echo "TEST END"
done
