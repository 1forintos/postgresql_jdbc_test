#!/usr/bin/python3
from multiprocessing import Process
from optparse import OptionParser
import shutil
import os
import sys
import subprocess

def main(argv):
    dbhost = ""
    user = ""
    password = ""
    NUMBER_OF_TABLES = 0
    NUMBER_OF_COLUMNS = 0
    NUMBER_OF_ROWS = 0
    multithreadOn = None

    usage = "usage: %prog -d <db_host> -u <db_user> -p <db_password> -t <num_of_tables> -c <num_of_cols> -r <num_of_rows> [-m]"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dbhost", dest="dbhost", help="database host", metavar="DBHOST")
    parser.add_option("-u", "--user", dest="user", help="database user", metavar="USER")
    parser.add_option("-p", "--password", dest="password", help="database password", metavar="PASSWORD")
    parser.add_option("-t", "--tablenum", dest="NUMBER_OF_TABLES", help="number of tables", metavar="TABLENUM")
    parser.add_option("-c", "--colnum", dest="NUMBER_OF_COLUMNS", help="number of columns per table", metavar="COLNUM")
    parser.add_option("-r", "--rownum", dest="NUMBER_OF_ROWS", help="number of rows per column", metavar="ROWNUM")
    parser.add_option("-m", "--multithread", action="store_true", dest="multithreadOn", help="allow multithreading", default=False)

    (options, args) = parser.parse_args()

    if not options.dbhost:
        parser.error("undefined database host")
    if not options.user:
        parser.error("undefined database user")
    if not options.password:
        parser.error("undefined database password")
    if not options.NUMBER_OF_TABLES:
        parser.error("undefined number of tables")
    if not options.NUMBER_OF_COLUMNS:
        parser.error("undefined number of columns")
    if not options.NUMBER_OF_ROWS:
        parser.error("undefined number of rows")

    dbhost = options.dbhost
    user = options.user
    password = options.password
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

    # generate table creator scripts
    for tableNum in range(1, NUMBER_OF_TABLES + 1):
        if multithreadOn:
            p1 = Process(target=genTableCreatorScript, args=(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS,))
            p1.start()
        else:
            genTableCreatorScript(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS)

    if multithreadOn:
        for i in range(0, tableNum):
            p1.join()

    # ececute table creator scripts
    for tableNum in range(1, NUMBER_OF_TABLES + 1):
        if multithreadOn:
            p2 = Process(target=executePsqlScript, args=(tableNum, dbhost, user, password,))
            p2.start()
        else:
            executePsqlScript(tableNum, dbhost, user, password)

    if multithreadOn:
        for i in range(0, tableNum):
            p2.join()

    print("Cleanup...")
    if os.path.exists("gen/"):
           shutil.rmtree("gen/")

    print("Done.")


def genTableCreatorScript(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS):
    print("Generating script for table " + str(tableNum) + " (pid:" + str(os.getpid()) + ")")

    file = open("gen/create_table" + str(tableNum) + ".sql", 'w')
    line = "DROP TABLE IF EXISTS table" + str(tableNum) + ";\n"
    file.write(line)
    line = "CREATE TABLE table" + str(tableNum) + " (\n"
    line += "    id serial PRIMARY KEY,\n"
    file.write(line)

    for colNum in range(1, NUMBER_OF_COLUMNS + 1):
        line = "    col" + str(colNum) + " varchar(100)"
        if colNum < NUMBER_OF_COLUMNS:
            line += ",\n";
        else:
            line += "\n"
        file.write(line)

    file.write(");\n\n")

    insertPart1 = ""
    insertPart2 = ""

    insertPart1 += "INSERT INTO table" + str(tableNum) + " ("
    for colNum in range(1, NUMBER_OF_COLUMNS + 1):
        insertPart1 += "col" + str(colNum);

        if colNum < NUMBER_OF_COLUMNS:
            insertPart1 += ", "
        else:
            insertPart1 += ") "

    for rowNum in range(1, NUMBER_OF_ROWS + 1):
        insertPart2 = "VALUES ("

        for colNum in range(1, NUMBER_OF_COLUMNS + 1):
            insertPart2 += "'value_" + str(tableNum) + "_" + str(colNum) + "_" + str(rowNum) + "'"
            if colNum < NUMBER_OF_COLUMNS:
                insertPart2 += ", "
            else:
                insertPart2 += ");"

        file.write(insertPart1)
        file.write(insertPart2)
        file.write("\n")

    file.close()

def executePsqlScript(scriptNum, dbhost, user, password):
    os.environ["PGPASSWORD"] = password
    print("Creating table " + str(scriptNum) + " (pid:" + str(os.getpid()) + ")")
    scriptPath = "gen/create_table" + str(scriptNum) + ".sql"
    FNULL = open(os.devnull, 'w')
    #
    subprocess.run(["psql", "-h", dbhost, "-U", user, "-f", scriptPath], stdout=FNULL, stderr=subprocess.STDOUT)


if __name__ == "__main__":
   main(sys.argv[1:])
