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
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Random;
import java.util.logging.FileHandler;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

public class DBClient {

	public static String URL = null; 
	public static String USER = "postgres";
	public static String PASSWORD = "postgres";
	public static int tableCount = 5;
	public static int colCount = 10;
	public static int rowCount = 180000;
	public static CSVRecord[] rowsToCheck = new CSVRecord[tableCount];
	public static List<String> colNames = new ArrayList<String>();
	public static List<String> tableNames = new ArrayList<String>();
	public static int tableNumToCheck;
	public static int rowNumToCheck;
	public static String csvRoot = "";
	public static Logger lgr = null;
	public static FileHandler logFh = null;
	public static String logsFolder = "logs/jdbc/";

	public static void main(String[] args) {
		initLogger();
		generateColumnNames();
		generateTableNames();
		if (args.length < 2) {
			logError("Required arguments: path to the root of CSV files that contain expected data, database host.");
			return;
		} else {
			Path path = Paths.get(args[0]);
			if (Files.notExists(path)) {
				log(args[0] + " is not a directory.");
				return;
			}
		}
		URL = "jdbc:postgresql://" + args[1] + ":5432/postgres";
		csvRoot = args[0];
		Random rand = new Random();
		rowNumToCheck = rand.nextInt(rowCount) + 1;
		int i = 0;
		for(int tableNum = 0; tableNum < tableCount; tableNum++) {
			String tableName = tableNames.get(tableNum);
			try {
				File csvData = new File(csvRoot + tableName + ".csv");
				CSVParser parser = CSVParser
						.parse(csvData, Charset.defaultCharset(), CSVFormat.EXCEL
								.withHeader(colNames.toArray(new String[0])));
				for (CSVRecord csvRecord : parser) {
					if (i == rowNumToCheck) {
						// System.out.println("Found row " + rowNumToCheck);
						// System.out.println(csvRecord.get(csvHeader.get(1)));
						rowsToCheck[tableNum] = csvRecord;
						i = 0;
						break;
					}
					i++;
				}
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

		while (!tablesExist());
		verifyRecords();
		System.exit(0);
	}

	private static String getTimeStamp() {
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS");
		Date now = new Date();
		String strDate = sdf.format(now);
		return strDate;
	}

	private static boolean tablesExist() {
		//log("Verifying tables existence...");

		boolean tablesExist = false;
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
			if(!ex.getSQLState().equals("08001")) {
				logError(ex.getMessage());
			}
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
				log(ex.getMessage());
				tablesExist = false;
			}
		}
		return tablesExist;
	}

	private static void verifyRecords() {
		
		Connection con = null;
		Statement st = null;
		ResultSet rs = null;
		boolean recordsMatch = true;
		try {
			for(int i = 0; i < tableCount; i++) {
				if(!recordsMatch) {
					break;
				}
				String tableName = tableNames.get(i);
				log("Checking row " + (rowNumToCheck + 1) + " from " + tableName + " ...");
				
				con = DriverManager.getConnection(URL, USER, PASSWORD);
				st = con.createStatement();
				rs = st.executeQuery("SELECT * FROM " + tableName
						+ " ORDER BY id LIMIT 1 OFFSET " + rowNumToCheck + ";");
				if (rs.next()) {
					for (String colName : colNames) {
						if (!(rowsToCheck[i].get(colName).toString()).equals(rs
								.getArray(colName).toString())) {
							logError("Error: Unexpected result found in table: ["
									+ tableName + "] at row: [" + rowNumToCheck
									+ "]");
							logError("Expected: ["
									+ rowsToCheck[i].get(colName).toString()
									+ "] | Received: ["
									+ rs.getArray(colName).toString() + "]");
							recordsMatch = false;
						} 
					}
				}
			}
		} catch (SQLException ex) {
			logError(ex.getMessage());
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
				logError(ex.getMessage());
			}
		}
		if(!recordsMatch) {
			System.exit(1);
		}
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

	private static void log(String logMsg) {
		lgr.info("[" + getTimeStamp() + "] " + logMsg);
	}

	private static void logError(String errMsg) {
		lgr.log(Level.SEVERE, "[" + getTimeStamp() + "] " + errMsg);
	}

	private static void initLogger() {
		File logFolder = new File(logsFolder);
		if (!logFolder.exists()) {
			logFolder.mkdirs();
		}
		SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd_HH_mm_ss.SSS");
		Date now = new Date();
		String strDate = sdf.format(now);
		String logFileRelPath = logsFolder + strDate + ".log";
		try {
			logFh = new FileHandler(logFileRelPath);
			lgr = Logger.getLogger(DBClient.class.getName());
			lgr.setUseParentHandlers(false);
			lgr.addHandler(logFh);
			SimpleFormatter formatter = new SimpleFormatter();
			logFh.setFormatter(formatter);
		} catch (SecurityException | IOException e) {
			System.out.println("Failed to create " + logFileRelPath);
			e.printStackTrace();
		}
	}
}
