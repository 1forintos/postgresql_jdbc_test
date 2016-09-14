#!/usr/bin/python3
'''
@author Márton Kamrás
'''

from multiprocessing import Process
from optparse import OptionParser
import shutil
import os
import sys
import subprocess
import time

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
    if os.path.exists("tmp/"):
        shutil.rmtree("tmp/")
    if os.path.exists("gen/"):
        shutil.rmtree("gen/")

    os.makedirs("tmp/")
    os.makedirs("gen/")

    tableNames = []
    # generate table creator scripts
    print("Generating table creator scripts...")
    for tableNum in range(1, NUMBER_OF_TABLES + 1):
        if multithreadOn:
            p1 = Process(target=genTableCreatorScript, args=(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS,))
            p1.start()
        else:
            genTableCreatorScript(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS)

        tableNames.append("table" + str(tableNum))

    if multithreadOn:
        for i in range(0, tableNum):
            p1.join()

    # ececute table creator scripts
    print("Creating tables...")
    os.environ["PGPASSWORD"] = password
    for tableNum in range(1, NUMBER_OF_TABLES + 1):
        scriptPath = "tmp/create_table" + str(tableNum) + ".sql"
        subprocessArgs = ["psql", "-h", dbhost, "-U", user, "-f", scriptPath]
        msg = "Creating table " + str(tableNum)
        if multithreadOn:
            p2 = Process(target=executePsqlScript, args=(subprocessArgs, msg, True, False))
            p2.start()
        else:
            executePsqlScript(subprocessArgs, msg, False, False)

    if multithreadOn:
        for i in range(0, tableNum):
            p2.join()

    # generate table verifying scripts
    print("Generating table verification scripts...")
    for tableName in tableNames:
        #if multithreadOn:
        #    p2 = Process(target=generateTableVerifyingScript, args=(tableName,))
        #    p2.start()
        #else:
        generateTableVerifyingScript(tableName)

    print("Verifying tables...")
    for tableNum in range(1, NUMBER_OF_TABLES + 1):
        scriptPath = "gen/verify_table" + str(tableNum) + ".sql"
        subprocessArgs = ["psql", "-h", dbhost, "-U", user, "-f", scriptPath]
        msg = "Verifying table " + str(tableNum)
        if multithreadOn:
            p2 = Process(target=executePsqlScript, args=(subprocessArgs, msg, True, True))
            p2.start()
        else:
            executePsqlScript(subprocessArgs, msg, False, True)

    p2.join()
    time.sleep(0.1)
    print("Cleanup...")
    if os.path.exists("tmp/"):
            shutil.rmtree("tmp/")
    #if os.path.exists("gen/"):
    #        shutil.rmtree("gen/")
    print("Finished.")

def genTableCreatorScript(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS):
    print("Generating script for table " + str(tableNum) + " (pid:" + str(os.getpid()) + ")")
    tableName = "table" + str(tableNum)
    file = open("tmp/create_table" + str(tableNum) + ".sql", 'w')
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

        file.write("BEGIN;")
        file.write(insertPart1)
        file.write(insertPart2)
        file.write("COMMIT;")
        file.write("\n")

    file.close()


def executePsqlScript(args, msg, multithreadOn, showOutput):
    if multithreadOn:
        msg += " (pid:" + str(os.getpid()) + ")"
    if msg is not None:
        print(msg)

    if showOutput:
        subprocess.run(args, stdout=sys.stdout, stderr=subprocess.STDOUT)
    else:
        FNULL = open(os.devnull, 'w')
        subprocess.run(args, stdout=FNULL, stderr=subprocess.STDOUT)

def generateTableVerifyingScript(tableName):
    line = "SELECT \'" + tableName + "\' as table_name, COUNT(*) as num_of_rows FROM " + tableName + ";"
    scriptPath = "gen/verify_" + tableName + ".sql"
    file = open(scriptPath, 'w')
    file.write(line)
    file.close()
    print("Generated \"" + scriptPath + "\"")

if __name__ == "__main__":
   main(sys.argv[1:])
