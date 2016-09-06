#!/usr/bin/python3

import shutil
import os

print("Preparing...")
if os.path.exists("gen/"):
	shutil.rmtree("gen/")

os.makedirs("gen/")

DATABASE_NAME = "testdb"
DATABASE_OWNER = "postgres"
NUMBER_OF_TABLES = 5
NUMBER_OF_COLUMNS = 10
NUMBER_OF_ROWS = 400

for tableNum in range(0, NUMBER_OF_TABLES):
	print("Generating script for table " + str(tableNum + 1))
	file = open("gen/create_table" + str(tableNum + 1) + ".sql", 'w')
	line = "DROP TABLE table" + str(tableNum + 1) + ";\n"
	file.write(line)

	line = "CREATE TABLE table" + str(tableNum + 1) + " (\n";
	file.write(line)

	for colNum in range(0, NUMBER_OF_COLUMNS):
		line = "	col" + str(colNum + 1) + " varchar(100)"
		if colNum + 1 < NUMBER_OF_COLUMNS:
			line += ",\n";
		else:
			line += "\n"
		file.write(line)

	file.write(");\n\n")

	insertPart1 = ""
	insertPart2 = ""

	insertPart1 += "INSERT INTO table" + str(tableNum + 1) + " ("
	for colNum in range(0, NUMBER_OF_COLUMNS):
		insertPart1 += "col" + str(colNum + 1);

		if colNum + 1 < NUMBER_OF_COLUMNS:
			insertPart1 += ", "
		else:
			insertPart1 += ") "

	for rowNum in range(0, NUMBER_OF_ROWS):
		insertPart2 = "VALUES ("

		for colNum in range(0, NUMBER_OF_COLUMNS):
			insertPart2 += "'value_" + str(tableNum + 1) + "_" + str(colNum + 1) + "_" + str(rowNum + 1) + "'"
			if colNum + 1 < NUMBER_OF_COLUMNS:
				insertPart2 += ", "
			else:
				insertPart2 += ");"

		file.write(insertPart1)
		file.write(insertPart2)
		file.write("\n")

	file.close()
