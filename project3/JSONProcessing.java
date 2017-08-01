import java.sql.*;
import java.util.Scanner;
import org.json.simple.*;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import org.json.simple.JSONArray;
import org.json.simple.parser.ParseException;
import java.io.FileReader;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.Iterator;
import java.util.Date;

public class JSONProcessing 
{
	public static void processJSON(String json) {

		System.out.println("-------- PostgreSQL " + "JDBC Connection Testing ------------");
        try {
            Class.forName("org.postgresql.Driver");
        } catch (ClassNotFoundException e) {
            System.out.println("Where is your PostgreSQL JDBC Driver? " + "Include in your library path!");
            e.printStackTrace();
            return;
        }

        System.out.println("PostgreSQL JDBC Driver Registered!");
        Connection connection = null;
        try {
            connection = DriverManager.getConnection("jdbc:postgresql://localhost:5432/flightsskewed","vagrant", "vagrant");
        } catch (SQLException e) {
            System.out.println("Connection Failed! Check output console");
            e.printStackTrace();
            return;
        }

        if (connection != null) {
            System.out.println("You made it, take control your database now!");
        } else {
            System.out.println("Failed to make connection!");
            return;
        }
        

		try{
			JSONParser parser = new JSONParser();
			Object obj = parser.parse(json);
			JSONObject jobject = (JSONObject)obj;

			String customerid = (String)jobject.get("customerid");
			//System.out.println("The cusid is :" + customerid);
			String name = (String)jobject.get("name");
			//System.out.println("The cusname is :" + name);
			String birthdate = (String)jobject.get("birthdate");
			//System.out.println("The cusbd is :" + birthdate);
			String frequentflieron = (String)jobject.get("frequentflieron");
			//System.out.println("The ff is :" + frequentflieron);
       		

			JSONObject structure = (JSONObject) jobject.get("newcustomer");
			String newcusid = (String)structure.get("customerid");
			String newcusname = (String)structure.get("name");
			String newcusbd = (String)structure.get("birthdate");
			//System.out.println("The cusbd is:" + newcusbd);
			String newcusflier = (String)structure.get("frequentflieron");

			Statement stmt = connection.createStatement();
			String sql = "select airlineid from airlines where name = " + "'" + newcusflier+ "'"+";";
			ResultSet rs = stmt.executeQuery(sql);
			while (rs.next()){
				String ff = rs.getString("airlineid");
				if(newcusid != null && newcusname != null && newcusbd != null && ff !=null){
				String sqlin = "insert into customers values('" + newcusid + "', '" + newcusname +"', '" + newcusbd + "', '" + ff + "');" ;
				Statement stmt2 = connection.createStatement();
				stmt2.executeUpdate(sqlin);
				}
			}
			stmt.close();
		}catch(ParseException e){
			e.printStackTrace();
		}catch(NullPointerException e){
			e.printStackTrace();
		}catch(SQLException e){
			e.printStackTrace();
		}
		

		try{
			JSONParser parser = new JSONParser();
			Object obj = parser.parse(json);
			JSONObject jobject = (JSONObject)obj;

			JSONObject structure = (JSONObject)jobject.get("flightinfo");
			String newflid = (String)structure.get("flightid");
			System.out.println("flightid is:" + newflid);
			String newfldt = (String)structure.get("flightdate");
			System.out.println("flightdate is:" + newfldt);

			JSONArray cuss = (JSONArray)structure.get("customers");
			
			//for(int i=0; i<cuss.size();i++){
			//	System.out.println("The" + i+ "element is: "+cuss.get(i));
			//}
			Iterator i = cuss.iterator();
			while(i.hasNext()){
				//System.out.println(i.next());
				JSONObject innerobj =(JSONObject) i.next();
				String cussid = (String)innerobj.get("customer_id");
				String cussna = (String)innerobj.get("name");
				String cussbd = (String)innerobj.get("birthdate");
				String cussff = (String)innerobj.get("frequentflieron");
				//System.out.println("Cusid is" + cussid + cussna+cussbd +cussff);
				Statement stmt0 = connection.createStatement();
				String sql0 = "select customerid from customers where customerid = '" + cussid + "';";
				ResultSet rs = stmt0.executeQuery(sql0);
				while (rs.next()){
					String customerid = rs.getString("customerid");
					//System.out.println("customerid exist :" + customerid);
					if(cussid == customerid){
					Statement stmt2 = connection.createStatement();
					String sql2 = "insert into flewon values ('" + newflid +"', '" + newfldt + "', '" + cussid + "'); ";
					stmt2.executeUpdate(sql2);
					}
					}
				if(cussna != null && cussbd != null && cussff != null ){
					//System.out.println(cussid);
					Statement stmt3 =  connection.createStatement();
					String sql3 = "insert into customers values ('" + cussid + "', '" + cussna + "','" + cussbd + "', '" + cussff + "')";
					stmt3.executeUpdate(sql3);
					Statement stmt4 = connection.createStatement();
					String sql4 = "insert into flewon values ('" + newflid +"', '" + newfldt + "', '" + cussid + "'); ";
					stmt4.executeUpdate(sql4);
				}
			}
		}catch(ParseException e){
			e.printStackTrace();
		}catch(NullPointerException e){
			e.printStackTrace();
		}catch(SQLException e){
			e.printStackTrace();
		}

		/************* 
		 * Add you code to insert appropriate tuples into the database.
		 ************/


		System.out.println("Adding data from " + json + " into the database");
	}

	public static void main(String[] argv) {

		Scanner in_scanner = new Scanner(System.in); //system.in is an input stream-reading from keyboard

		while(in_scanner.hasNext()) {
			String json = in_scanner.nextLine();
			processJSON(json);
		}
	}
}
