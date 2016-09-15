package postgres.dbclient;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.logging.Level;
import java.util.logging.Logger;

public class DBClient {
	
	public static String URL = "jdbc:postgresql://172.17.0.2:5432/postgres";
	public static String USER = "postgres";
	public static String PASSWORD = "postgres";
	public static String[] tableNames = {"table1", "table2", "table3", "table4", "table5"};
	
	public static void main(String[] args) {
		while(!tablesExist());
		while(true) {
			getLastNRecordsFromTable(1000, "table3");
		}
		
	} 
	
	private static boolean tablesExist() {
		Logger lgr = Logger.getLogger(DBClient.class.getName());
		lgr.log(Level.INFO, "Verifying tables existence...");
		
		boolean tablesExist = true; // TODO rename exists
		Connection con = null;
		Statement st = null;
		ResultSet rs = null;
		
		try {
			con = DriverManager.getConnection(URL, USER, PASSWORD);
			for (String tableName : tableNames) {
				st = con.createStatement();
				rs = st.executeQuery("SELECT count(*) AS row_count FROM " + tableName);
				if(rs.next()) {
					int rowCount = rs.getInt("row_count");
					if(rowCount != 60000) {
						lgr.log(Level.SEVERE, "Unexpected count of rows in [" + tableName + "]");
						tablesExist = false;
					}
				}
				/*if(rs.next()) {
					if(!rs.getBoolean(1)) {
						lgr.log(Level.SEVERE, "Table does not exist: " + tableName);
						tablesExist = false;
					} else {
						// lgr.log(Level.INFO, "Table [" + tableName + "] exists.");
					}
				}*/
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

	private static void getLastNRecordsFromTable(int n, String tableName) {
		Logger lgr = Logger.getLogger(DBClient.class.getName());
		lgr.log(Level.INFO, "Selecting " + n + " records from " + tableName);
		
		Connection con = null;
		Statement st = null;
		ResultSet rs = null;
		
		try {
			con = DriverManager.getConnection(URL, USER, PASSWORD);
			st = con.createStatement();
			rs = st.executeQuery("SELECT * FROM " + tableName + " LIMIT " + n + " OFFSET 50;");
			rs = st.executeQuery("SELECT count(*) AS row_count FROM " + tableName);
			if(rs.next()) {
				System.out.println(rs.getInt("row_count"));
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
	}
}
