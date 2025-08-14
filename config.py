import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file or from /workspace/uploads/.env as fallback
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists('/workspace/uploads/.env'):
    load_dotenv('/workspace/uploads/.env')

class Config:
    # SQL Server Configuration
    SQL_SERVER = os.environ.get('SQL_SERVER', '(localdb)\MSSQLLocalDB')
    SQL_DATABASE = os.environ.get('SQL_DATABASE', 'InventoryDB2')
    # SQL_USERNAME = os.environ.get('SQL_USERNAME', 'sa')
    # SQL_PASSWORD = os.environ.get('SQL_PASSWORD', 'YourStrong@Passw0rd')
    SQL_DRIVER = os.environ.get('SQL_DRIVER', 'ODBC Driver 17 for SQL Server')
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-testing')
    
    # Build connection string
    connection_string = (
        f"DRIVER={{{SQL_DRIVER}}};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
    )
    
   
    
    connection_string += "TrustServerCertificate=yes;"
    
    # URL encode the connection string for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_string)}"
    
    # # Alternative connection using pytds
    # SQLALCHEMY_DATABASE_URI_PYTDS = f"mssql+pytds://{SQL_USERNAME}:{SQL_PASSWORD}@{SQL_SERVER}/{SQL_DATABASE}"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False