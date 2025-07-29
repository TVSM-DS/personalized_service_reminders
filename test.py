
import os
from databricks.sql import connect as databricks_connect
import traceback # Import traceback for detailed error logging

def connect_to_databricks():
    """
    Establishes a connection to the Databricks SQL Warehouse.
    Retrieves connection details from environment variables.
    Returns a connection object if successful, None otherwise.
    """
    # Retrieve Databricks connection details from environment variables
    # These variables are expected to be loaded into the environment
    # (e.g., from a .env file using load_dotenv() at the application's entry point).
    DB_SERVER_HOSTNAME = os.getenv("DATABRICKS_SERVER_HOSTNAME")
    DB_HTTP_PATH = os.getenv("DATABRICKS_HTTP_PATH")
    DB_ACCESS_TOKEN = os.getenv("DATABRICKS_TOKEN")
    print(DB_ACCESS_TOKEN)
    # Validate that all necessary environment variables are set
    if not all([DB_SERVER_HOSTNAME, DB_HTTP_PATH, DB_ACCESS_TOKEN]):
        print("Error: Databricks connection details (HOSTNAME, HTTP_PATH, or TOKEN) are not fully set in environment variables.")
        print("Please ensure your .env file is correctly configured and loaded, or environment variables are set.")
        return None
    
    try:
        # Attempt to establish the connection using the databricks-sql-connector
        connection = databricks_connect(
            server_hostname=DB_SERVER_HOSTNAME,
            http_path=DB_HTTP_PATH,
            access_token=DB_ACCESS_TOKEN
        )
        print("Successfully established connection to Databricks SQL Warehouse.")
        return connection
    except Exception as e:
        # Catch any exceptions that occur during the connection attempt
        # Print the full traceback for detailed debugging information
        traceback.print_exc() 
        print(f"Error connecting to Databricks: {e}")
        return None

# Example Usage (for testing the function independently):
if __name__ == "__main__":
    # In a real application, load_dotenv() would typically be called
    # at the very beginning of your main script.
    # For this standalone example, we'll load it here if a .env file exists.
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Environment variables loaded from .env file (if present).")
    except ImportError:
        print("python-dotenv not installed. Ensure environment variables are set manually.")

    # Call the function to get a connection
    db_connection = connect_to_databricks()

    if db_connection:
        print("\nDatabase connection obtained successfully!")
        # You can now use db_connection for your database operations
        # For example, execute a simple query:
        try:
            with db_connection.cursor() as cursor:
                cursor.execute("SELECT current_user()")
                user = cursor.fetchone()
                print(f"Connected as user: {user[0]}")
        except Exception as e:
            print(f"Error executing test query: {e}")
        finally:
            # Always ensure the connection is closed when you're done with it
            db_connection.close()
            print("Database connection closed.")
    else:
        print("\nFailed to obtain a database connection.")
        print("Please check the error messages above for details on why the connection failed.")
