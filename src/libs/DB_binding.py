# Attention! 
# Your local computer need copy file "example.env" and replace to ".env" and write db host, database_name, user, passwordS

import psycopg2
from psycopg2.extras import DictCursor

import os
from dotenv import load_dotenv
load_dotenv('././.env')

class DB_binding:
    connect = None
    def Connect(self):
        db_host = os.environ.get('DB_HOST')
        db_name = os.environ.get('DB_NAME')
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')

        self.connect = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        self.connect.autocommit = True

    def Disconnect(self):
        self.connect.close()
        self.connect = None

    def Sql(self, sql_query):
        if not self.connect:
            self.Connect()

        cursor = self.connect.cursor(cursor_factory=DictCursor)

        with self.connect.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(sql_query)

            res_0 = cursor.fetchall()

            res = []
            for row in res_0:
                res.append(dict(row))

            return res
    
    # Gets

    def Get_user_id_from_tg_user_id(self):
        # return self.Sql("")
        pass

    def Get_current_queue(self):
        # return self.Sql("")
        pass

    def Get_current_sessions(self):
        # return self.Sql("")
        pass

    def Get_current_counts_msg_in_sessions(self):
        # return self.Sql("")
        pass

    # Adds

    def Add_user(self, tg_user_id, social_credit):
        self.Sql(f"INSERT INTO users(tg_user_id, social_credit) VALUES ({tg_user_id}, {social_credit});")

    def Add_queue(self, user_id, time_start):
        self.Sql(f"INSERT INTO queue(user_id, time_start) VALUES ({user_id}, {time_start});")

    def Add_session(self):
        # self.Sql("")
        pass

    def Add_log(self):
        # self.Sql("")
        pass

    # Updates


# Debug

a = DB_binding()
b = a.Sql("SELECT * FROM users;")
for row in b:
    print(row)
