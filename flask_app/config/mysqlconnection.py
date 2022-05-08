import pymysql.cursors
import os

class MySQLConnection:
    def __init__(self, db):
        self.connection = pymysql.connect(
            host = os.getenv("host"),
            user = os.getenv("user"), 
            password = os.getenv("password"),#YOUR PASSWORD HERE INSTEAD OF 'root'
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

def create_db():
    connection = pymysql.connect(
        host = os.getenv("host"),
        user = os.getenv("user"),
        password = os.getenv("password")
    )
    connection.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{os.getenv('db_name')}`;")
    connection.select_db(os.getenv('db_name'))

    connection.cursor().execute(f"CREATE TABLE IF NOT EXISTS `users` (`id` int NOT NULL AUTO_INCREMENT,`email` varchar(255) NOT NULL,`password_hash` char(60) NOT NULL,`account_level` int NOT NULL DEFAULT '1',PRIMARY KEY (`id`),UNIQUE KEY `email_UNIQUE` (`email`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;")

    connection.cursor().execute("CREATE TABLE IF NOT EXISTS `terminals` (`id` int NOT NULL AUTO_INCREMENT,`name` varchar(45) NOT NULL,`auth_email` varchar(255) DEFAULT NULL,`auth_password` varchar(255) DEFAULT NULL,`auth_url` varchar(255) DEFAULT NULL,`auth_required` tinyint NOT NULL DEFAULT '0',`data_url` varchar(255) NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `name_UNIQUE` (`name`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;")

    connection.cursor().execute("CREATE TABLE IF NOT EXISTS `ssls` (`id` int NOT NULL AUTO_INCREMENT,`name` varchar(5) NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `name_UNIQUE` (`name`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;")

    connection.cursor().execute("CREATE TABLE IF NOT EXISTS `containers` (`id` int NOT NULL AUTO_INCREMENT,`size` varchar(25) NOT NULL,PRIMARY KEY (`id`),UNIQUE KEY `size_UNIQUE` (`size`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;")

    connection.cursor().execute("CREATE TABLE IF NOT EXISTS `availabilities` (`id` int NOT NULL AUTO_INCREMENT,`terminal_id` int NOT NULL,`container_id` int NOT NULL,`ssl_id` int NOT NULL,`created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,`type` set('Pick','Drop') NOT NULL,PRIMARY KEY (`id`),KEY `fk_partnership_has_containers_containers1_idx` (`container_id`),KEY `fk_availabilities_terminals1_idx` (`terminal_id`),KEY `fk_availabilities_ssls1_idx` (`ssl_id`),CONSTRAINT `fk_availabilities_ssls1` FOREIGN KEY (`ssl_id`) REFERENCES `ssls` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,CONSTRAINT `fk_availabilities_terminals1` FOREIGN KEY (`terminal_id`) REFERENCES `terminals` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,CONSTRAINT `fk_partnership_has_containers_containers1` FOREIGN KEY (`container_id`) REFERENCES `containers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;")

    try:
        connection.cursor().execute(f"INSERT INTO `users` VALUES (1,'{os.getenv('owner_email')}','{os.getenv('owner_pw_hash')}',3);")
        connection.cursor().execute(f"INSERT INTO `terminals` VALUES (1,'t18','{os.getenv('j_username')}','{os.getenv('j_password')}','https://t18.tideworks.com/fc-T18/j_spring_security_check',1,'https://t18.tideworks.com/fc-T18/home/default.do?method=page&id=4'),(2,'t30','{os.getenv('j_username')}','{os.getenv('j_password')}','https://t30.tideworks.com/fc-T30/j_spring_security_check',1,'https://t30.tideworks.com/fc-T30/home/default.do'),(3,'t5','{os.getenv('j_username')}','{os.getenv('j_password')}','https://t5s.tideworks.com/fc-T5S/j_spring_security_check',1,'https://t5s.tideworks.com/fc-T5S/home/default.do?method=page&id=4'),(4,'wut',NULL,NULL,NULL,0,'https://www.uswut.com/schedule/empty-receiving/'),(5,'husky',NULL,NULL,NULL,0,'https://huskyterminal.com/');")
        connection.cursor().execute("INSERT INTO `containers` VALUES (1,'20DR/20SD'),(2,'20RFR/20RH'),(4,'40DH/40HC'),(3,'40DR/40SD'),(5,'40RFR/40RH'),(6,'45DH/45HC'),(7,'Special');")
        connection.cursor().execute("INSERT INTO `ssls` VALUES (1,'ANL'),(2,'APL'),(3,'CHV'),(4,'CMA'),(5,'COS'),(6,'EGL'),(7,'HAP'),(8,'HDM'),(10,'HLC'),(9,'HMM'),(11,'MAE'),(12,'MSC'),(13,'ONE'),(14,'OOCL'),(15,'PAI'),(16,'SAF'),(17,'SEA'),(18,'SMC'),(19,'SUD'),(20,'WHL'),(21,'WWS'),(22,'YML'),(23,'ZIM');")
        connection.commit()
    except Exception as e:
        print("Something went wrong" , e)
    finally:
        connection.close()

def connectToMySQL(db):
    return MySQLConnection(db)