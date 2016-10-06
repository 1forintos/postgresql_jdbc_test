/*
 * testlibpq.c
 *
 *      Test the C version of libpq, the PostgreSQL frontend library.
 */
#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>

static void
exit_nicely(PGconn *conn)
{
    PQfinish(conn);
    exit(1);
}

int
main(int argc, char **argv)
{
    const char *connString;
    PGconn     *conn;
    PGresult   *res;
    int         nFields;
    int         i,
                j;

    const char *pghost = "localhost";
    const char *pgport = "5432";
    const char *pgoptions = "";
    const char *pgtty = "";
    const char *dbName = "postgres";
    const char *login = "postgres";
    const char *pwd = "postgres";

    /*
     * If the user supplies a parameter on the command line, use it as the
     * conninfo string; otherwise default to setting dbname=postgres and using
     * environment variables or defaults for all other connection parameters.
     */
    if (argc > 1)
        connString = argv[1];
    else
        connString = "postgresql://postgres@172.17.0.2:5432";

    unsigned int pingResult = PQping(connString);
    switch (pingResult) {
        case PQPING_OK:
            fprintf(stdout, "PQPING_OK\n");
            break;
        case PQPING_REJECT:
            fprintf(stdout, "PQPING_REJECT\n");
            break;
        case PQPING_NO_RESPONSE:
            fprintf(stdout, "PQPING_NO_RESPONSE\n");
            break;
        case PQPING_NO_ATTEMPT:
            fprintf(stdout, "PQPING_NO_ATTEMPT\n");
            break;
        default:
            fprintf(stdout, "NOTHING ZOMG\n");
            break;
    }
    /* Make a connection to the database */
    //conn = PQconnectdb(conninfo);
    // conn = *PQsetdbLogin(pghost, pgport, pgoptions, pgtty, dbName, login, pwd);

    /* Check to see that the backend connection was successfully made */
    /*if (PQstatus(conn) != CONNECTION_OK)
    {
        fprintf(stderr, "Connection to database failed: %s",
                PQerrorMessage(conn));
        exit_nicely(conn);
    }
*/
    /*
     * Our test case here involves using a cursor, for which we must be inside
     * a transaction block.  We could do the whole thing with a single
     * PQexec() of "select * from pg_database", but that's too trivial to make
     * a good example.
     */

    /* Start a transaction block */
    /*res = PQexec(conn, "BEGIN");
    if (PQresultStatus(res) != PGRES_COMMAND_OK)
    {
        fprintf(stderr, "BEGIN command failed: %s", PQerrorMessage(conn));
        PQclear(res);
        exit_nicely(conn);
    }*/

    /*
     * Should PQclear PGresult whenever it is no longer needed to avoid memory
     * leaks
     */
    //PQclear(res);

    /*
     * Fetch rows from pg_database, the system catalog of databases
     */
    /*res = PQexec(conn, "DECLARE myportal CURSOR FOR select * from distributors");
    if (PQresultStatus(res) != PGRES_COMMAND_OK)
    {
        fprintf(stderr, "DECLARE CURSOR failed: %s", PQerrorMessage(conn));
        PQclear(res);
        exit_nicely(conn);
    }
    PQclear(res);

    res = PQexec(conn, "FETCH ALL in myportal");
    if (PQresultStatus(res) != PGRES_TUPLES_OK)
    {
        fprintf(stderr, "FETCH ALL failed: %s", PQerrorMessage(conn));
        PQclear(res);
        exit_nicely(conn);
    }
*/
    /* first, print out the attribute names */
    /*nFields = PQnfields(res);
    for (i = 0; i < nFields; i++)
        printf("%-15s", PQfname(res, i));
    printf("\n\n");
*/
    /* next, print out the rows */
    /*for (i = 0; i < PQntuples(res); i++)
    {
        for (j = 0; j < nFields; j++)
            printf("%-15s", PQgetvalue(res, i, j));
        printf("\n");
    }

    PQclear(res);
*/
    /* close the portal ... we don't bother to check for errors ... */
/*    res = PQexec(conn, "CLOSE myportal");
    PQclear(res);
*/
    /* end the transaction */
    /*res = PQexec(conn, "END");
    PQclear(res);
*/
    /* close the connection to the database and cleanup */
    //PQfinish(conn);

    return 0;
}
