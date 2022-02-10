class Bot_logic:
    send = None # def send(tg_user_id, send_message)
    db = None # DB_binding()
    modify_msg = None # MessageHandler()

    def init(self):
        pass

    def handler_start(self, tg_user_id):
        users_counts = len(self.db.Sql("SELECT * FROM users;"))
        
        self.send(tg_user_id,  
        f''' 
Hello, World! :3
Users counts: {users_counts}
        ''')
        
        if not self.db.Get_id_from_tg_user_id(tg_user_id):
            self.db.Add_user(tg_user_id, 0)
            self.send(tg_user_id,f"You added own database")

    def handler_message(self, tg_user_id, message):
        modified_msg = self.modify_msg(message)

        msg_start = ""
        msg_end = ""

        print(modified_msg)

        for row in modified_msg:
            print(row)
            print(len(row))
            print(type(row))
            
            msg_start += row[0] + "\n\n"
            msg_end += row[1] + "\n"
        
        self.send(tg_user_id, msg_start+msg_end)

    