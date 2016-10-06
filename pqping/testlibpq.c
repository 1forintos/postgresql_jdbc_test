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

unsigned int main(int argc, char **argv)
{
    const char *connString;
    PGconn     *conn;
    PGresult   *res;
    int         nFields;
    int         i, j;

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
    /*
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
    */

    return pingResult;
}
