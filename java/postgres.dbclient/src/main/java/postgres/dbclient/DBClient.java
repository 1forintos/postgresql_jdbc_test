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
		if(tablesExist()) {
			
		}
	}
	
	private static boolean tablesExist() {
		boolean tablesExist = true;
		
		Connection con = null;
		Statement st = null;
		ResultSet rs = null;
		
		try {
			con = DriverManager.getConnection(URL, USER, PASSWORD);
			for (String tableName : tableNames) {
				st = con.createStatement();
				rs = st.executeQuery("SELECT EXISTS ("
						+ "SELECT 1 "
						+ "FROM information_schema.tables "
						+ "WHERE table_name = '" + tableName + "'"
						+ ");");
				if(rs.next()) {
					if(!rs.getBoolean(1)) {
						Logger lgr = Logger.getLogger(DBClient.class.getName());
						lgr.log(Level.SEVERE, "Table does not exist: " + tableName);
						tablesExist = false;
					}
				}
			}

		} catch (SQLException ex) {
			Logger lgr = Logger.getLogger(DBClient.class.getName());
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
				Logger lgr = Logger.getLogger(DBClient.class.getName());
				lgr.log(Level.WARNING, ex.getMessage(), ex);
				tablesExist = false;
			}
		}
		return tablesExist;
	}
}
