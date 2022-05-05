import pymysql.cursors

class MySQLConnection:
    def __init__(self, db):
        self.connection = pymysql.connect(
            host = 'localhost',
            user = 'root', 
            password = 'root',#YOUR PASSWORD HERE INSTEAD OF 'root'
            db = db,
            charset = 'utf8mb4',
            cursorclass = pymysql.cursors.DictCursor,
            autocommit = True
        )
    def query_db(self, query, data = None):
        with self.connection.cursor() as cursor:
            try:
                # Combines the data dictionary with the query string and formats it
                query = cursor.mogrify(query.lower(), data).replace("\\","").strip()
                print("Running Query: ", query)
                # Execute the query on our MySQL server
                cursor.execute(query)

                if query.startswith("select"):
                    # SELECT queries will return any matching rows from the database as a LIST OF DICTIONARIES
                    # If no rows match the query, the function will return an EMPTY TUPLE
                    return cursor.fetchall()
                elif query.startswith("insert"):
                    # INSERT queries will return the ID of the new row inserted
                    return cursor.lastrowid
                # UPDATE and DELETE queries will return None
            except Exception as e:
                # If your query fails for any reason, print the error and return False
                print("Something went wrong", e)
                return False
            finally:
                self.connection.close()

def connectToMySQL(db):
    return MySQLConnection(db)