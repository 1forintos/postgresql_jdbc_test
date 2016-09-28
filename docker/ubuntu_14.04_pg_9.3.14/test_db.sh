#!/bin/sh
while true
do
	echo "TEST BEGIN"
	docker exec postgres_9.3.14 free && sync && free
	docker exec postgres_9.3.14 service postgresql stop
	docker exec postgres_9.3.14 service postgresql start &

	result=-1
	echo "Trying to run query..."
	while [ $result -ne 0 ]
	do
	        psql -h $1 -q -U postgres -c "SELECT * FROM table2 ORDER BY id LIMIT 1 OFFSET 10;" ; result=$?
	done
	sleep 2
	echo "Query succeeded."
	echo "TEST END"
done
