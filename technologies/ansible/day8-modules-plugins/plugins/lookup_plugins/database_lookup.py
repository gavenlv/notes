# -*- coding: utf-8 -*-

"""
Database lookup plugin for Ansible
Allows querying databases and returning results
"""

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError, AnsibleParserError
from ansible.utils.display import Display

display = Display()

class LookupModule(LookupBase):
    """
    Database lookup plugin
    
    Supports multiple database types:
    - PostgreSQL
    - MySQL
    - SQLite
    - MongoDB (basic queries)
    """
    
    def run(self, terms, variables=None, **kwargs):
        """
        Execute database lookup
        
        Args:
            terms: List of SQL queries to execute
            variables: Ansible variables
            **kwargs: Database connection parameters
        
        Returns:
            List of query results
        """
        
        # Get connection parameters
        db_type = kwargs.get('type', 'postgresql').lower()
        host = kwargs.get('host', 'localhost')
        port = kwargs.get('port')
        database = kwargs.get('database', 'postgres')
        username = kwargs.get('username', 'postgres')
        password = kwargs.get('password', '')
        
        # Set default ports
        if port is None:
            default_ports = {
                'postgresql': 5432,
                'mysql': 3306,
                'sqlite': None,
                'mongodb': 27017
            }
            port = default_ports.get(db_type)
        
        results = []
        
        try:
            if db_type == 'postgresql':
                results = self._query_postgresql(terms, host, port, database, username, password)
            elif db_type == 'mysql':
                results = self._query_mysql(terms, host, port, database, username, password)
            elif db_type == 'sqlite':
                results = self._query_sqlite(terms, database)
            elif db_type == 'mongodb':
                results = self._query_mongodb(terms, host, port, database, username, password)
            else:
                raise AnsibleError(f"Unsupported database type: {db_type}")
                
        except Exception as e:
            raise AnsibleError(f"Database lookup failed: {str(e)}")
        
        return results
    
    def _query_postgresql(self, terms, host, port, database, username, password):
        """Query PostgreSQL database"""
        try:
            import psycopg2
            import psycopg2.extras
        except ImportError:
            raise AnsibleError("psycopg2 library is required for PostgreSQL queries")
        
        results = []
        
        try:
            # Establish connection
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Execute queries
            for query in terms:
                display.vvv(f"Executing PostgreSQL query: {query}")
                cursor.execute(query)
                
                if cursor.description:
                    # SELECT query
                    rows = cursor.fetchall()
                    results.extend([dict(row) for row in rows])
                else:
                    # INSERT/UPDATE/DELETE query
                    results.append({'affected_rows': cursor.rowcount})
            
            conn.commit()
            conn.close()
            
        except psycopg2.Error as e:
            raise AnsibleError(f"PostgreSQL error: {str(e)}")
        
        return results
    
    def _query_mysql(self, terms, host, port, database, username, password):
        """Query MySQL database"""
        try:
            import mysql.connector
        except ImportError:
            raise AnsibleError("mysql-connector-python library is required for MySQL queries")
        
        results = []
        
        try:
            # Establish connection
            conn = mysql.connector.connect(
                host=host,
                port=port,
                database=database,
                user=username,
                password=password
            )
            
            cursor = conn.cursor(dictionary=True)
            
            # Execute queries
            for query in terms:
                display.vvv(f"Executing MySQL query: {query}")
                cursor.execute(query)
                
                if cursor.description:
                    # SELECT query
                    rows = cursor.fetchall()
                    results.extend(rows)
                else:
                    # INSERT/UPDATE/DELETE query
                    results.append({'affected_rows': cursor.rowcount})
            
            conn.commit()
            conn.close()
            
        except mysql.connector.Error as e:
            raise AnsibleError(f"MySQL error: {str(e)}")
        
        return results
    
    def _query_sqlite(self, terms, database_path):
        """Query SQLite database"""
        try:
            import sqlite3
        except ImportError:
            raise AnsibleError("sqlite3 library is required for SQLite queries")
        
        results = []
        
        try:
            # Establish connection
            conn = sqlite3.connect(database_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            cursor = conn.cursor()
            
            # Execute queries
            for query in terms:
                display.vvv(f"Executing SQLite query: {query}")
                cursor.execute(query)
                
                if query.strip().upper().startswith('SELECT'):
                    # SELECT query
                    rows = cursor.fetchall()
                    results.extend([dict(row) for row in rows])
                else:
                    # INSERT/UPDATE/DELETE query
                    results.append({'affected_rows': cursor.rowcount})
            
            conn.commit()
            conn.close()
            
        except sqlite3.Error as e:
            raise AnsibleError(f"SQLite error: {str(e)}")
        
        return results
    
    def _query_mongodb(self, terms, host, port, database, username, password):
        """Query MongoDB database"""
        try:
            from pymongo import MongoClient
        except ImportError:
            raise AnsibleError("pymongo library is required for MongoDB queries")
        
        results = []
        
        try:
            # Build connection string
            if username and password:
                connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
            else:
                connection_string = f"mongodb://{host}:{port}/{database}"
            
            # Establish connection
            client = MongoClient(connection_string)
            db = client[database]
            
            # Execute queries
            for query_info in terms:
                if isinstance(query_info, str):
                    # Simple find query
                    collection_name = query_info
                    cursor = db[collection_name].find()
                    results.extend(list(cursor))
                elif isinstance(query_info, dict):
                    # Complex query
                    collection_name = query_info.get('collection')
                    operation = query_info.get('operation', 'find')
                    query = query_info.get('query', {})
                    projection = query_info.get('projection', None)
                    
                    collection = db[collection_name]
                    
                    if operation == 'find':
                        cursor = collection.find(query, projection)
                        results.extend(list(cursor))
                    elif operation == 'find_one':
                        result = collection.find_one(query, projection)
                        if result:
                            results.append(result)
                    elif operation == 'count':
                        count = collection.count_documents(query)
                        results.append({'count': count})
                    else:
                        raise AnsibleError(f"Unsupported MongoDB operation: {operation}")
                else:
                    raise AnsibleError("Invalid MongoDB query format")
            
            client.close()
            
        except Exception as e:
            raise AnsibleError(f"MongoDB error: {str(e)}")
        
        return results

# Example usage in playbooks:
"""
# PostgreSQL example
- name: Get user data from PostgreSQL
  debug:
    msg: "{{ lookup('database', 'SELECT * FROM users WHERE active = true', 
                    type='postgresql', host='localhost', database='myapp', 
                    username='readonly', password='secret') }}"

# MySQL example
- name: Get product count from MySQL
  debug:
    msg: "{{ lookup('database', 'SELECT COUNT(*) as total FROM products', 
                    type='mysql', host='db.example.com', database='inventory', 
                    username='reader', password='pass123') }}"

# SQLite example
- name: Query local SQLite database
  debug:
    msg: "{{ lookup('database', 'SELECT name, email FROM contacts', 
                    type='sqlite', database='/path/to/database.db') }}"

# MongoDB example
- name: Get MongoDB documents
  debug:
    msg: "{{ lookup('database', 
                    {'collection': 'users', 'operation': 'find', 'query': {'status': 'active'}},
                    type='mongodb', host='localhost', database='myapp') }}"
""" 