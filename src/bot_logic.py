import schedule, time, random

class Bot_logic:
    send = None # def send(tg_user_id, send_message)
    db = None # DB_binding()
    modify_msg = None # MessageHandler()

    current_queue = [] # [{'queue_id':0, 'tg_user_id':0, 'time_start':0, 'last_companion': 0}, ...]
    current_sessions = [] # [{'session_id':0 ,'tg_user_id_a': 0, 'tg_user_id_b': 0, 'time_start': 0}, ...]

    def init(self):
        current_queue = self.db.Get_current_queue()
        for v in current_queue:
            tg_user_id = self.db.Get_tg_user_id_from_id(v['user_id'])
            last_companion = self.db.Get_last_companion(tg_user_id)
            self.current_queue.append({'queue_id': v["id"], 'tg_user_id': tg_user_id, 'time_start': v['time_start'].timestamp(), 'last_companion': last_companion})

        current_sessions = self.db.Get_current_sessions()
        for v in current_sessions:
            tg_user_id_a = self.db.Get_tg_user_id_from_id(v['user_id_a'])
            tg_user_id_b = self.db.Get_tg_user_id_from_id(v['user_id_b'])
            self.current_sessions.append({'session_id': v["id"], 'tg_user_id_a': tg_user_id_a, 'tg_user_id_b': tg_user_id_b, 'time_start': v['time_start'].timestamp()})

        schedule.every(5).seconds.do(self.queue_schedule)

        self.commands = {
            'start': self.cmd_start,
            'stop': self.cmd_stop
        }

    # handlers

    def handler_commands(self, command_name, tg_user_id):
        self.commands[command_name](tg_user_id)
        print("run command")

    def handler_message(self, tg_user_id, message):
        
        time_send = time.time()
        session_id = None
        tg_user_id_companion = None

        for session in self.current_sessions:

            for k in session.keys():
                print(f"{k}\n")
            print()

            if session['tg_user_id_a'] == tg_user_id:
                tg_user_id_companion = session['tg_user_id_b']
                session_id = session['session_id']
                break
            if session['tg_user_id_b'] == tg_user_id:
                tg_user_id_companion = session['tg_user_id_a']
                session_id = session['session_id']
                break
            
        if session_id:
            # time.sleep(0)
            self.send(tg_user_id_companion, message) # <--- add random put bot message
            self.db.Add_log(tg_user_id, session_id, message, time_send, "original", 0)
        else:
            self.send(tg_user_id,  self.modify_msg(message), parse_mode='Markdown')
    
    # schedulers

    def queue_schedule(self):
        time_stemp = int(time.time()*1000)/1000
        
        will_be_connection = {} # {'tg_user_id_a': ['tg_user_id_b','tg_user_id_c'], ... }

        for user_a in self.current_queue:
            waiting_time = time_stemp - user_a['time_start']
            if waiting_time > 10:
                for user_b in self.current_queue:
                    id_a = user_a['tg_user_id']
                    id_b = user_b['tg_user_id']

                    if ((id_a != id_b) and 
                        (user_a['last_companion'] != id_b or
                        waiting_time > 30 ) and
                        ( not will_be_connection.get(id_b) ) ):

                        if not will_be_connection.get(id_a):
                            will_be_connection[id_a] = []
                        will_be_connection[id_a].append(id_b)


        for tg_user_id_a, list_users_b in will_be_connection.items():
            tg_user_id_b = random.choice(list_users_b)

            self.send(tg_user_id_a, '---\nCompanion found!\nPlease, send message.\n---')
            self.send(tg_user_id_b, '---\nCompanion found!\nPlease, send message.\n---')

            self.add_to_sessions(tg_user_id_a, tg_user_id_b, time_stemp)

    # commands

    def cmd_start(self, tg_user_id):
        time_stemp = int(time.time()*1000)/1000
        if not self.db.Get_id_from_tg_user_id(tg_user_id):
            self.db.Add_user(tg_user_id, 0)
            self.send(tg_user_id,f"Приветственное сообщение, если здесь впервые.")

        # users_counts = len(self.db.Sql("SELECT * FROM users;"))
        queue_counts = len(self.current_queue)
        session_counts = len(self.current_sessions)*2
        self.send(tg_user_id, f'Online users:\nin queue - {queue_counts}\nin sessions - {session_counts}\n')
        self.send(tg_user_id, f'Please wait at least 10 seconds...')

        self.add_to_queue(tg_user_id, time_stemp)

    def cmd_stop(self, tg_user_id):
        time_stemp = int(time.time()*1000)/1000
        self.stop_session(tg_user_id, time_stemp, "command_stop")

    # utils

    def add_to_queue(self, tg_user_id, time_stemp):
        for user_in_queue in self.current_queue:
            if user_in_queue['tg_user_id'] == tg_user_id:
                return

        self.db.Add_queue(tg_user_id, time_stemp)

        queue_id = self.db.Get_queue_id_from_time_start(time_stemp)
        last_companion = self.db.Get_last_companion(tg_user_id)
        self.current_queue.append({'queue_id': queue_id,'tg_user_id': tg_user_id, 'time_start': time_stemp, 'last_companion': last_companion})

    def add_to_sessions(self, tg_user_id_a, tg_user_id_b, time_stemp):
        self.db.Add_session(tg_user_id_a, tg_user_id_b, time_stemp)

        session_id = self.db.Get_session_id_from_time_start(time_stemp)
        self.current_sessions.append({'session_id': session_id, 'tg_user_id_a': tg_user_id_a, 'tg_user_id_b': tg_user_id_b, 'time_start': time_stemp})
        
        self.stop_queue(tg_user_id_a, tg_user_id_b, time_stemp, session_id)

    def stop_queue(self, tg_user_id_a, tg_user_id_b, time_stemp, session_id):
        for user_in_queue in self.current_queue:
            if user_in_queue['tg_user_id'] == tg_user_id_a or user_in_queue['tg_user_id'] ==  tg_user_id_b:
                self.db.Stop_queue(user_in_queue['queue_id'], time_stemp, session_id)
                self.current_queue.remove(user_in_queue)

    def stop_session(self, tg_user_id, time_stemp, status):
        for session in self.current_sessions:
            if (session['tg_user_id_a'] == tg_user_id or
                session['tg_user_id_b'] == tg_user_id ):
                self.db.Stop_session(session['session_id'], time_stemp, status)
                self.current_sessions.remove(session)
