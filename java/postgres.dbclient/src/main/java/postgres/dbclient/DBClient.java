package postgres.dbclient;

import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Random;
import java.util.logging.Level;
import java.util.logging.Logger;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

public class DBClient {
	
	public static CSVRecord rowToCheck = null;
	public static String URL = "jdbc:postgresql://172.17.0.2:5432/postgres";
	public static String USER = "postgres";
	public static String PASSWORD = "postgres";
	public static int tableCount = 5;
	public static int colCount = 10;
	public static int rowCount = 180000;
	public static List<String> colNames = new ArrayList<String>();
	public static List<String> tableNames = new ArrayList<String>();
	public static int tableNumToCheck;
	public static int rowNumToCheck;
	public static String tableName = null;
	public static String csvRoot = "";
	public static Logger lgr = Logger.getLogger(DBClient.class.getName());

	public static void main(String[] args) {
		getTimeStamp();
		generateColumnNames();
		generateTableNames();

		if (args.length < 1) {
			lgr.log(Level.SEVERE,
					"Undefined path to the root of CSV files that contain expected data.");
			return;
		} else {
			Path path = Paths.get(args[0]);
			if (Files.notExists(path)) {
				lgr.log(Level.SEVERE, args[0] + " is not a directory.");
				return;
			}
		}
		csvRoot = args[0];
		Random rand = new Random();
		tableNumToCheck = rand.nextInt(tableCount) + 1;
		rowNumToCheck = rand.nextInt(rowCount) + 1;
		tableName = tableNames.get(tableNumToCheck - 1);
		File csvData = new File(csvRoot + tableName + ".csv");
		int i = 0;
		CSVRecord csvHeader = null;
		try {
			CSVParser parser = CSVParser
					.parse(csvData, Charset.defaultCharset(), CSVFormat.EXCEL
							.withHeader(colNames.toArray(new String[0])));
			for (CSVRecord csvRecord : parser) {
				if (csvHeader == null) {
					csvHeader = csvRecord;
				} else if (i == rowNumToCheck) {
					// System.out.println("Found row " + rowNumToCheck);
					// System.out.println(csvRecord.get(csvHeader.get(1)));
					rowToCheck = csvRecord;
					break;
				}
				i++;
			}
		} catch (IOException e) {
			e.printStackTrace();
		}

		while (!tablesExist());
		while (!expectedRecordReceived());
	}

	private static String getTimeStamp() {
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
		Date now = new Date();
	    String strDate = sdf.format(now);
		return strDate;
	}

	private static boolean tablesExist() {
		lgr.log(Level.INFO, "Verifying tables existence...");

		boolean tablesExist = false; // TODO rename exists
		Connection con = null;
		Statement st = null;
		ResultSet rs = null;

		try {
			con = DriverManager.getConnection(URL, USER, PASSWORD);
			for (String tableName : tableNames) {
				st = con.createStatement();
				rs = st.executeQuery("SELECT count(*) AS row_count FROM "
						+ tableName);
				if (rs.next()) {
					int rowCount = rs.getInt("row_count");
					if (rowCount > 0) {
						tablesExist = true;
					}
				}
			}

		} catch (SQLException ex) {
			lgr.log(Level.SEVERE, ex.getMessage(), ex);
			tablesExist = false;
		} finally {
			try {
				if (rs != null) {
					rs.close();
				}
				if (st != null) {
					st.close();
				}
				if (con != null) {
					con.close();
				}

			} catch (SQLException ex) {
				lgr.log(Level.WARNING, ex.getMessage(), ex);
				tablesExist = false;
			}
		}
		return tablesExist;
	}

	private static boolean expectedRecordReceived() {
		Logger lgr = Logger.getLogger(DBClient.class.getName());
		lgr.log(Level.INFO, "Checking row " + (rowNumToCheck + 1) + " from " + tableName + " ...");

		Connection con = null;
		Statement st = null;
		ResultSet rs = null;
		boolean expectedRecordFound = false;
		try {
			con = DriverManager.getConnection(URL, USER, PASSWORD);
			st = con.createStatement();
			rs = st.executeQuery("SELECT * FROM " + tableName
					+ " ORDER BY id LIMIT 1 OFFSET " + rowNumToCheck + ";");
			if (rs.next()) {
				for(String colName : colNames) {
					if(!(rowToCheck.get(colName).toString()).equals(rs.getArray(colName).toString())) {
						lgr.log(Level.SEVERE, "Error: Unexpected result found in table: [" + tableName + "] at row: [" + rowNumToCheck + "]");
					} else {
						expectedRecordFound = true;
					}
				}
				
			}
		} catch (SQLException ex) {
			lgr.log(Level.SEVERE, ex.getMessage(), ex);
		} finally {
			try {
				if (rs != null) {
					rs.close();
				}
				if (st != null) {
					st.close();
				}
				if (con != null) {
					con.close();
				}

			} catch (SQLException ex) {
				lgr.log(Level.WARNING, ex.getMessage(), ex);
			}
		}
		
		return expectedRecordFound;
	}

	private static void generateTableNames() {
		for (int i = 0; i < tableCount; i++) {
			tableNames.add("table" + (i + 1));
		}

	}

	private static void generateColumnNames() {
		for (int i = 0; i < colCount; i++) {
			colNames.add("col" + (i + 1));
		}
	}
}
