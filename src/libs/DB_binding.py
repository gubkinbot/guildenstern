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
    
    def Get_queue_id_from_time_start(self, time_start):
        id = self.Sql(f"SELECT id, EXTRACT(epoch FROM time_start) FROM queue WHERE {time_start} = EXTRACT(epoch FROM time_start);")
        return None if id == [] else id[0]['id']

    def Get_session_id_from_time_start(self, time_start):
        id = self.Sql(f"SELECT id, EXTRACT(epoch FROM time_start) FROM sessions WHERE {time_start} = EXTRACT(epoch FROM time_start);")
        return None if id == [] else id[0]['id']

    def Get_current_queue(self):
        return self.Sql(f"SELECT * FROM queue WHERE time_stop IS NULL;")

    def Get_current_sessions(self):
        return self.Sql(f"SELECT * FROM sessions WHERE time_stop IS NULL;")

    # def Get_current_counts_msg_in_sessions(self):
    #     # return self.Sql("")
    #     pass
    
    def Get_last_companion(self, tg_user_id):
        user_id = self.Get_id_from_tg_user_id(tg_user_id)

        last_companion = None # self.Sql("") # <>

        return last_companion if last_companion else 0

    # Adds

    def Add_user(self, tg_user_id, social_credit):
        self.Sql(f"INSERT INTO users(tg_user_id, social_credit) VALUES ({tg_user_id}, {social_credit});")

    def Add_queue(self, tg_user_id, time_start):
        user_id = self.Get_id_from_tg_user_id(tg_user_id)
        time_start = int(time_start*1000)/1000
        self.Sql(f"INSERT INTO queue(user_id, time_start) VALUES ({user_id}, to_timestamp({time_start}));")

    def Add_session(self, tg_user_id_a, tg_user_id_b, time_start):
        user_id_a = self.Get_id_from_tg_user_id(tg_user_id_a)
        user_id_b = self.Get_id_from_tg_user_id(tg_user_id_b)
        time_start = int(time_start*1000)/1000
        self.Sql(f"INSERT INTO sessions(user_id_a, user_id_b, time_start) VALUES ({user_id_a}, {user_id_b}, to_timestamp({time_start}));")

    def Add_log(self, tg_user_id, session_id, message, time_send, type, grade):
        user_id = self.Get_id_from_tg_user_id(tg_user_id)
        time_send = int(time_send*1000)/1000
        self.Sql(f"INSERT INTO log(user_id, session_id, message, time_send, type, grade) VALUES ({user_id}, {session_id}, '{message}', to_timestamp({time_send}), '{type}', {grade});")

    def Add_points(self, tg_user_id, delta_points, time_event):
        user_id = self.Get_id_from_tg_user_id(tg_user_id)
        time_event = int(time_event*1000)/1000
        self.Sql(f"INSERT INTO points(user_id, delta_points, time_event) VALUES ({user_id}, {delta_points}, to_timestamp({time_event}) );")

    # Updates

    def Stop_queue(self, queue_id, time_stop, session_id):
        self.Sql(f"UPDATE queue SET time_stop = {time_stop}, session_id = {session_id} WHERE id = {queue_id};")

    # def Stop_queue_without_session_id(self, queue_id, time_stop, session_id):

    def Stop_session(self, session_id, time_stop, status):
        self.Sql(f"UPDATE queue SET time_stop = {time_stop}, status = {status} WHERE id = {session_id};")

# Debug

#import time
#db = DB_binding()

# b = db.Sql("SELECT * FROM users;")
# for row in b:
#     print(row)

# db.Add_queue(439699346, time.time())

# print(db.Get_id_from_tg_user_id(439699346))
