#!/usr/bin/python3
from multiprocessing import Process
from optparse import OptionParser
import shutil
import os
import sys

def main(argv):
    NUMBER_OF_TABLES = 0
    NUMBER_OF_COLUMNS = 0
    NUMBER_OF_ROWS = 0
    multithreadOn = None

    usage = "usage: %prog -t <num_of_tables> -c <num_of_cols> -r <num_of_rows> [-m]"
    parser = OptionParser(usage)
    parser.add_option("-t", "--tablenum", dest="NUMBER_OF_TABLES", help="number of tables", metavar="TABLENUM")
    parser.add_option("-c", "--colnum", dest="NUMBER_OF_COLUMNS", help="number of columns per table", metavar="COLNUM")
    parser.add_option("-r", "--rownum", dest="NUMBER_OF_ROWS", help="number of rows per column", metavar="ROWNUM")
    parser.add_option("-m", "--multithread", action="store_true", dest="multithreadOn", help="allow multithreading", default=False)

    (options, args) = parser.parse_args()

    if not options.NUMBER_OF_TABLES:
        parser.error("undefined number of tables")
    if not options.NUMBER_OF_COLUMNS:
        parser.error("undefined number of columns")
    if not options.NUMBER_OF_ROWS:
        parser.error("undefined number of rows")

    NUMBER_OF_TABLES = int(options.NUMBER_OF_TABLES)
    NUMBER_OF_COLUMNS = int(options.NUMBER_OF_COLUMNS)
    NUMBER_OF_ROWS = int(options.NUMBER_OF_ROWS)
    multithreadOn = bool(options.multithreadOn)

    if multithreadOn:
        print("Multithreading On")
    else:
        print("Multithreading Off")

    print("Preparing...")
    if os.path.exists("gen/"):
        shutil.rmtree("gen/")

    os.makedirs("gen/")

    for tableNum in range(0, NUMBER_OF_TABLES):
        if multithreadOn:
            p = Process(target=genTableCreatorScript, args=(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS,))
            p.start()
        else:
            genTableCreatorScript(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS)

    if multithreadOn:
        p.join()

    print("Cleanup...")
    if os.path.exists("gen/"):
   	    shutil.rmtree("gen/")    

    print("Done.")


def genTableCreatorScript(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS):
	print("Generating script for table " + str(tableNum + 1) + " (pid:" + str(os.getpid()) + ")")

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

def executePsqlScript(host, user, password, d):
	'''psql -h 172.17.0.2 -U postgres -W -f create_tables.sql'''

if __name__ == "__main__":
   main(sys.argv[1:])
