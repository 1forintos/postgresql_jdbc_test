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
import csv
from enum import Enum

class Phase(Enum):
    all = 0
    generateSql = 1
    runSql = 2
    generateCsv = 3


def main(argv):
    dbhost = ""
    user = ""
    password = ""
    NUMBER_OF_TABLES = 0
    NUMBER_OF_COLUMNS = 0
    NUMBER_OF_ROWS = 0
    phase = 0
    multithreadOn = None
    saveCsv = None

    usage = "usage: %prog -d <db_host> -u <db_user> -p <db_password> -t <num_of_tables> -c <num_of_cols> -r <num_of_rows> --phase <phase_to_run> [-m]"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dbhost", dest="dbhost", help="database host", metavar="DBHOST")
    parser.add_option("-u", "--user", dest="user", help="database user", metavar="USER")
    parser.add_option("-p", "--password", dest="password", help="database password", metavar="PASSWORD")
    parser.add_option("-t", "--tablenum", dest="NUMBER_OF_TABLES", help="number of tables", metavar="TABLENUM")
    parser.add_option("-c", "--colnum", dest="NUMBER_OF_COLUMNS", help="number of columns per table", metavar="COLNUM")
    parser.add_option("-r", "--rownum", dest="NUMBER_OF_ROWS", help="number of rows per column", metavar="ROWNUM")
    parser.add_option("--phase", dest="phase", help="phase to run ["
        + str(Phase.all.value) + ": all, "
        + str(Phase.generateSql.value) + ": generate table creator scripts, "
        + str(Phase.runSql.value) + ": insert tables into database, "
        + str(Phase.generateCsv.value) + ": generate csv file from tables] Default=0", metavar="PHASE", default=str(Phase.all.value))
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

    try:
        phase = int(options.phase)
    except ValueError:
        parser.error("phase parameter has to be an integer.")

    if not (phase == Phase.all.value
        or phase == Phase.generateSql.value
        or phase == Phase.runSql.value
        or phase == Phase.generateCsv.value):
        parser.error("invalid phase parameter (possible values: ["
            + str(Phase.all.value) + ","
            + str(Phase.generateSql.value) + ","
            + str(Phase.runSql.value) + ","
            + str(Phase.generateCsv.value) + "], default="
            + str(Phase.all.value) + ")")

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
    if os.path.exists("gen/") and phase == Phase.all.value:
        shutil.rmtree("gen/")
    if os.path.exists("gen/sql/") and phase == Phase.generateSql.value:
        shutil.rmtree("gen/sql/")
    if os.path.exists("gen/csv/") and phase == Phase.generateCsv.value:
        shutil.rmtree("gen/csv/")
    elif (not os.path.exists("gen/sql/")) and phase == Phase.runSql.value:
        print("Error: missing SQL scripts. (Run phase " + str(Phase.generateSql.value) + " to generate SQL scripts.)")
        exit()

    if phase == Phase.all.value:
        os.makedirs("gen/sql/")
        os.makedirs("gen/csv/")
    elif phase == Phase.generateSql.value:
        os.makedirs("gen/sql/")
    elif phase == Phase.generateCsv.value:
        os.makedirs("gen/csv/")

    # ------------------------ GENERATE SQL ------------------------
    if phase == Phase.all.value or phase == Phase.generateSql.value:
        # generate table creator scripts
        print("Generating table creator scripts...")
        for tableNum in range(1, NUMBER_OF_TABLES + 1):
            if multithreadOn:
                p1 = Process(target=genTableCreatorScript, args=(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS))
                p1.start()
            else:
                genTableCreatorScript(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS)

        if multithreadOn:
            for i in range(0, tableNum):
                p1.join()

    # ------------------------ GENERATE CSV ------------------------
    if phase == Phase.all.value or phase == Phase.generateCsv.value:
        print("Generating CSV files...")
        for tableNum in range(1, NUMBER_OF_TABLES + 1):
            if multithreadOn:
                p1 = Process(target=genCsvFile, args=(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS))
                p1.start()
            else:
                genCsvFile(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS)

        if multithreadOn:
            for i in range(0, tableNum):
                p1.join()

    # ------------------------ EXECUTE SQL ------------------------
    if phase == Phase.all.value or phase == Phase.runSql.value:
        # ececute table creator scripts
        print("Creating tables...")
        os.environ["PGPASSWORD"] = password
        for tableNum in range(1, NUMBER_OF_TABLES + 1):
            scriptPath = "gen/sql/create_table" + str(tableNum) + ".sql"
            subprocessArgs = ["psql", "-h", dbhost, "-U", user, "-f", scriptPath, "-1"]
            msg = "Creating table " + str(tableNum)
            if multithreadOn:
                p2 = Process(target=executePsqlScript, args=(subprocessArgs, msg, True, False))
                p2.start()
            else:
                executePsqlScript(subprocessArgs, msg, False, False)

        if multithreadOn:
            for i in range(0, tableNum):
                p2.join()

    time.sleep(0.1)
    print("Finished.")

def genTableCreatorScript(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS):
    file = None
    tableName = "table" + str(tableNum)

    print("Generating SQL for table " + str(tableNum) + " (pid:" + str(os.getpid()) + ")")
    file = open("gen/sql/create_table" + str(tableNum) + ".sql", 'w')
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

    file.write("BEGIN;")
    for rowNum in range(1, NUMBER_OF_ROWS + 1):
        insertPart2 = "VALUES ("

        for colNum in range(1, NUMBER_OF_COLUMNS + 1):
            data = "value_" + str(tableNum) + "_" + str(colNum) + "_" + str(rowNum)
            insertPart2 += "'" + data + "'"
            if colNum < NUMBER_OF_COLUMNS:
                insertPart2 += ", "
            else:
                insertPart2 += ");"

        file.write(insertPart1)
        file.write(insertPart2)
        file.write("\n")

    file.write("COMMIT;")
    file.close()


def genCsvFile(tableNum, NUMBER_OF_COLUMNS, NUMBER_OF_ROWS):
    file = None
    csvFile = None
    csvWriter = None
    tableName = "table" + str(tableNum)

    print("Generating CSV for table " + str(tableNum) + " (pid:" + str(os.getpid()) + ")")
    csvFile = open("gen/csv/table" + str(tableNum) + ".csv", 'w')
    csvWriter = csv.writer(csvFile, delimiter=',')
    
    for rowNum in range(1, NUMBER_OF_ROWS + 1):
        csvRowData = []
        for colNum in range(1, NUMBER_OF_COLUMNS + 1):
            data = "value_" + str(tableNum) + "_" + str(colNum) + "_" + str(rowNum)
            csvRowData.append(data)

        csvWriter.writerow(csvRowData)

    csvFile.close()

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

if __name__ == "__main__":
   main(sys.argv[1:])
