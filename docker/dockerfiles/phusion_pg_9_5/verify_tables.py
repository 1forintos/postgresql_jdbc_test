#!/usr/bin/python3
'''
@author Márton Kamrás

This script verifies the existence of "tableN" (N=[1,2,..,NUMBER_OF_TABLES]) in
a PostgreSQL database.
'''

from multiprocessing import Process
from optparse import OptionParser
import shutil
import os
import sys
import subprocess

def main(argv):

    dbhost = ""
    user = ""
    NUMBER_OF_TABLES = 0
    multithreadOn = None

    usage = "usage: %prog -d <db_host> -u <db_user> -t <num_of_tables> [-m]"
    parser = OptionParser(usage)
    parser.add_option("-d", "--dbhost", dest="dbhost", help="database host", metavar="DBHOST")
    parser.add_option("-u", "--user", dest="user", help="database user", metavar="USER")
    parser.add_option("-t", "--tablenum", dest="NUMBER_OF_TABLES", help="number of tables", metavar="TABLENUM")
    parser.add_option("-m", "--multithread", action="store_true", dest="multithreadOn", help="allow multithreading", default=False)

    (options, args) = parser.parse_args()

    if not options.dbhost:
        parser.error("undefined database host")
    if not options.user:
        parser.error("undefined database user")
    if not options.NUMBER_OF_TABLES:
        parser.error("undefined number of tables")

    dbhost = options.dbhost
    user = options.user
    NUMBER_OF_TABLES = int(options.NUMBER_OF_TABLES)
    multithreadOn = bool(options.multithreadOn)

    if multithreadOn:
        print("Multithreading On")
    else:
        print("Multithreading Off")

    print("Preparing...")
    if os.path.exists("gen/"):
        shutil.rmtree("gen/")

    os.makedirs("gen/")

    # generate table verifying scripts
    print("Generating table verification scripts...")
    for tableNum in range(1, NUMBER_OF_TABLES + 1):
        tableName = "table" + str(tableNum)
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
