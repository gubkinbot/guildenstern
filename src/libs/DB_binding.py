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

            try:
                res_0 = cursor.fetchall()
            except Exception as e:
                print(f"Error: sql_query: {sql_query}")
                print(e)
                return None

            res = []
            for row in res_0:
                res.append(dict(row))

            return res
    
    # Gets

    def Get_id_from_tg_user_id(self, tg_user_id):
        id = self.Sql(f"SELECT id FROM users WHERE tg_user_id = {tg_user_id};")
        return None if id == [] else id[0]['id']
    
    def Get_id_from_time_start_queue(self):
        # return self.Sql("")
        pass

    def Get_id_from_time_start_session(self):
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

    def Add_session(self, user_id_a, user_id_b, time_start):
        self.Sql(f"INSERT INTO sessions(user_id_a, user_id_b, time_start) VALUES ({user_id_a}, {user_id_b}, {time_start});")

    def Add_log(self, user_id, session_id, message, time_send, type, grade):
        self.Sql(f"INSERT INTO log(user_id, session_id, message, time_send, type, grade) VALUES ({user_id}, {session_id}, '{message}', {time_send}, '{type}', {grade});")

    def Add_points(self, user_id, delta_points, time_event):
        self.Sql(f"INSERT INTO points(user_id, delta_points, time_event) VALUES ({user_id}, {delta_points}, {time_event});")

    # Updates


# Debug

# db = DB_binding()
# b = db.Sql("SELECT * FROM users;")
# for row in b:
#     print(row)

# print(db.Get_id_from_tg_user_id(439699346))
