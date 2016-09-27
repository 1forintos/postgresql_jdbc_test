#!/bin/sh
while true
do
	echo "TEST BEGIN"
	sudo docker exec postgres_9.3.14 free && sync && free
	sudo docker exec postgres_9.3.14 service postgresql stop
	sudo docker exec postgres_9.3.14 nice -n 19 service postgresql start &

	result=-1
	echo "Trying to run query..."
	while [ $result -ne 0 ]
	do
	        psql -h 172.17.0.2 -q -U postgres -c "SELECT * FROM table2 ORDER BY id LIMIT 1 OFFSET 80000;" ; result=$?
	done
	sleep 2
	echo "Query succeeded."
	echo "TEST END"
done
