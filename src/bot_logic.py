class Bot_logic:
    send = None # bot.send_message
    db = None # DB_binding

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


    