import schedule
import time

class Bot_logic:
    send = None # def send(tg_user_id, send_message)
    db = None # DB_binding()
    modify_msg = None # MessageHandler()

    def init(self):
        # get current queue
        # get current sessions

        schedule.every(5).seconds.do(self.queue_schedule)

        self.commands = {
            'start': self.cmd_start, 
        }

    def handler_commands(self, command_name, tg_user_id):
        self.commands[command_name](tg_user_id)

    def handler_message(self, tg_user_id, message):
        self.send(tg_user_id,  self.modify_msg(message))

    def queue_schedule(self):
        print( int(time.time()) )
        pass

    def cmd_start(self, tg_user_id):
        if not self.db.Get_id_from_tg_user_id(tg_user_id):
            self.db.Add_user(tg_user_id, 0)
            self.send(tg_user_id,f"Приветственное сообщение, если здесь впервые.")

        # users_counts = len(self.db.Sql("SELECT * FROM users;"))
        queue_counts = 0
        session_counts = 0
        self.send(tg_user_id, f'Online users:\nin queue - {queue_counts}\nin conversations - {session_counts}')
    
    def schedule_checker():
        while True:
            schedule.run_pending()
            time.sleep(1)