import schedule, time, random
from libs.models.nickname_generator import generate_nickname
# from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class Bot_logic:

    MIN_WAITING_IN_QUEUE = 3
    MAX_WAITING_IN_QUEUE = 60
    
    MAX_WAITING_IN_SESSIONS = 30

    COMPANION_TIME_OUT = 30 
    # Предел времи ожидания в очереди, для прошлого собеседника 
    # (если только они в двоем в очереди, через это время соеденит)
    # MIN_WAITING_IN_QUEUE < it < MAX_WAITING_IN_QUEUE


    send = None # def send(tg_user_id, send_message)
    delete = None # def send(tg_user_id, message_id)
    db = None # DB_binding()
    modify_msg = None # MessageHandler()
    create_buttons = None # create_buttons()

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
        schedule.every(10).seconds.do(self.timeouts_schedule)

        self.commands = {
            'start': self.cmd_start,
            'stop': self.cmd_stop,
            'search': self.cmd_start,
            'info': self.cmd_info,
            'test': self.cmd_test
        }

    # handlers

    def handler_commands(self, command_name, tg_user_id):
        self.commands[command_name](tg_user_id)


    impudence = [] # [{'session_id': 0, 'message_id': 0, 'arr': []}]
    is_bot = [] # [{'session_id': 0, 'message_id': 0, 'text': "", 'time_send': 0}]

    def handler_message(self, tg_user_id, message, is_callback_button = False):

        # if message.lower()[:6] == '/start':
        #     self.commands['start'](tg_user_id)
        #     return
        # if message.lower()[:5] == '/stop':
        #     self.commands['stop'](tg_user_id)
        #     return

        time_send = int(time.time()*1000)/1000
        session_id = None
        tg_user_id_companion = None

        for session in self.current_sessions:
            if session['tg_user_id_a'] == tg_user_id:
                tg_user_id_companion = session['tg_user_id_b']
                session_id = session['session_id']
                break
            if session['tg_user_id_b'] == tg_user_id:
                tg_user_id_companion = session['tg_user_id_a']
                session_id = session['session_id']
                break
            
        if session_id:

            if is_callback_button:
                # time.sleep(0)

                data = message.split(';')
                selected_id = int(data[0])

                if data[1] == 'impudence':
                    impud = {}
                    for v in self.impudence[:]:
                        if v['session_id'] == session_id:
                            impud = v
                            break
                    
                    self.delete(tg_user_id, impud['message_id'])
                    impudence_msg = impud['arr'][selected_id]
                    self.send(tg_user_id, f"---\nYou send:\n {impudence_msg}\n---")
                    self.send(tg_user_id_companion, impudence_msg)
                    self.db.Add_log(tg_user_id, session_id, impudence_msg, time_send, "from_bot", 0)

                    self.impudence.remove(impud)

                if data[1] == 'is_bot':
                    detected_bot = {}
                    for v in self.is_bot[:]:
                        if v['tg_user_id'] == tg_user_id:
                            detected_bot = v
                            break
                    
                    self.edit(chat_id = tg_user_id, message_id = detected_bot['message_id'], text = detected_bot['text'])
                    
                    self.db.Change_grade(detected_bot['time_send'], 1)

                    self.is_bot.remove(detected_bot)
            else: 
                # markup = InlineKeyboardMarkup()
                # markup.row_width = 3
                # markup.add(InlineKeyboardButton('1', callback_data='1_'), InlineKeyboardButton('2', callback_data='2_'), InlineKeyboardButton('3', callback_data='3_'))
                # self.send(tg_user_id_companion, self.modify_msg.process(message), parse_mode='Markdown', reply_markup=markup)
                
                #

                detected_bot = {}

                for v in self.is_bot[:]:
                    if v['tg_user_id'] == tg_user_id_companion:
                        detected_bot = v
                        break

                if detected_bot != {}:
                    self.edit(chat_id = tg_user_id_companion, message_id = detected_bot['message_id'], text = detected_bot['text'])
                    self.is_bot.remove(detected_bot)  

                #   
                
                send_message = self.modify_msg.preprocess(message)
                msg = self.send(tg_user_id_companion, send_message, parse_mode='Markdown', reply_markup = self.create_buttons(['🤖'], "is_bot"))
                self.is_bot.append({'tg_user_id': tg_user_id_companion, 'message_id': msg.message_id, 'text': send_message, 'time_send': time_send})
                
                #print(f"send buttons: {session_id}, {tg_user_id_companion}, {msg.message_id}, {send_message}")
                
                # self.send(tg_user_id, self.modify_msg.preprocess(message), parse_mode='Markdown')
                self.db.Add_log(tg_user_id, session_id, message, time_send, "original", 0)
    
                impudence = self.modify_msg.impudence(message)
                if impudence:
                    
                    msg_for_select = f"---\nPlease select message:"
                    for k, v in enumerate(impudence):
                        msg_for_select += f"\n\n{k+1} - " + v
                    msg_for_select += f"\n---"

                    msg = self.send( tg_user_id_companion, msg_for_select, reply_markup = self.create_buttons(['1','2','3'], "impudence"))
                    self.impudence.append({'session_id': session_id, 'message_id': msg.message_id, 'arr': impudence})
        else:
            self.send(tg_user_id,  self.modify_msg.process(message), parse_mode='Markdown')
            self.send(tg_user_id,  self.modify_msg.fuckoff(), parse_mode='Markdown')
    
    # schedulers

    def queue_schedule(self):
        time_stemp = int(time.time()*1000)/1000
        
        will_be_connection = {} # {'tg_user_id_a': ['tg_user_id_b','tg_user_id_c'], ... }

        for user_a in self.current_queue:
            waiting_time_a = time_stemp - user_a['time_start']
            if waiting_time_a > self.MIN_WAITING_IN_QUEUE:
                for user_b in self.current_queue:
                    id_a = user_a['tg_user_id']
                    id_b = user_b['tg_user_id']
                    waiting_time_b = time_stemp - user_b['time_start']

                    if ((id_a != id_b) and 
                        (user_a['last_companion'] != id_b or 
                        (waiting_time_a > self.COMPANION_TIME_OUT and
                         waiting_time_b > self.COMPANION_TIME_OUT)) and
                        (waiting_time_b > self.MIN_WAITING_IN_QUEUE) and
                        ( not will_be_connection.get(id_b) ) ):

                        if not will_be_connection.get(id_a):
                            will_be_connection[id_a] = []
                        will_be_connection[id_a].append(id_b)


        for tg_user_id_a, list_users_b in will_be_connection.items():
            tg_user_id_b = random.choice(list_users_b)

            self.add_to_sessions(tg_user_id_a, tg_user_id_b, time_stemp)

    def timeouts_schedule(self):
        time_stemp = int(time.time()*1000)/1000

        for user_in_queue in self.current_queue:
            waiting_time = time_stemp - user_in_queue['time_start']
            if waiting_time > self.MAX_WAITING_IN_QUEUE:
                tg_user_id = user_in_queue['tg_user_id']
                self.stop_queue(tg_user_id, tg_user_id, time_stemp, "NULL", '---\nTimeout search. Please repeat /start\n---')

        for session in self.current_sessions:
            last_message_timestamp = self.db.Get_last_message_timestamp_from_session_id(session['session_id'])
            if not last_message_timestamp:
                last_message_timestamp = session['time_start']
            waiting_time = time_stemp - last_message_timestamp
            if waiting_time > self.MAX_WAITING_IN_QUEUE:
                tg_user_id = session['tg_user_id_a']
                self.stop_session(tg_user_id, time_stemp, f"Timeout({self.MAX_WAITING_IN_SESSIONS})", '---\nTimeout session. Please repeat /start\n---')

    # commands

    def cmd_start(self, tg_user_id):
        time_stemp = int(time.time()*1000)/1000
        if not self.db.Get_id_from_tg_user_id(tg_user_id):
            # сюда надо пихнуть выгрузку уже существующих ников из базы
            #names = self.db.some_method()
            names = []
            nick = generate_nickname()
            while nick in names:
                nick = generate_nickname()
            self.db.Add_user(tg_user_id, 0)
            # сюда впихнуть сохранение никнейма в базу
            self.send(tg_user_id,f"Приветственное сообщение, если здесь впервые. \nНачать - /start\bОстановить - /stop\nБольше информации - /info")
            time.sleep(1)

        self.add_to_queue(tg_user_id, time_stemp)

    def cmd_stop(self, tg_user_id):
        time_stemp = int(time.time()*1000)/1000
        self.stop_queue(tg_user_id, tg_user_id, time_stemp, "NULL", '---\nSearch stopped. Please write /start\n---')
        self.stop_session(tg_user_id, time_stemp, "command_stop", '---\nSession stopped. Please write /start\n---')

    def cmd_info(self, tg_user_id):
        self.send(tg_user_id,f"Начать - /start\nОстановить - /stop\nБольше информации - /info")
        self.send(tg_user_id,f"Правила: (...)")
        self.send_online(tg_user_id)

    def cmd_test(self, tg_user_id):
        self.modify_msg.flag = True

    # utils

    def send_online(self, tg_user_id):
        # users_counts = len(self.db.Sql("SELECT * FROM users;"))
        queue_counts = len(self.current_queue)
        session_counts = len(self.current_sessions)*2
        self.send(tg_user_id, f'Online users:\nin queue - {queue_counts}\nin sessions - {session_counts}\n')

    def add_to_queue(self, tg_user_id, time_stemp):
        for user_in_queue in self.current_queue:
            if user_in_queue['tg_user_id'] == tg_user_id:
                return

        for sessions in self.current_sessions:
            if (sessions['tg_user_id_a'] == tg_user_id or
                sessions['tg_user_id_b'] == tg_user_id):
                self.send(tg_user_id, "---\nYou are in session, please write /stop and repeate /start.\n---")
                return

        self.send_online(tg_user_id)
        self.send(tg_user_id, f'Please wait...') # f'Please wait at least {self.MIN_WAITING_IN_QUEUE} seconds...')

        self.db.Add_queue(tg_user_id, time_stemp)

        queue_id = self.db.Get_queue_id_from_time_start(time_stemp)
        last_companion = self.db.Get_last_companion(tg_user_id)
        self.current_queue.append({'queue_id': queue_id,'tg_user_id': tg_user_id, 'time_start': time_stemp, 'last_companion': last_companion})

    def add_to_sessions(self, tg_user_id_a, tg_user_id_b, time_stemp):
        self.db.Add_session(tg_user_id_a, tg_user_id_b, time_stemp)

        session_id = self.db.Get_session_id_from_time_start(time_stemp)
        self.current_sessions.append({'session_id': session_id, 'tg_user_id_a': tg_user_id_a, 'tg_user_id_b': tg_user_id_b, 'time_start': time_stemp})
        
        self.stop_queue(tg_user_id_a, tg_user_id_b, time_stemp, session_id, '---\nCompanion found!\nPlease, send message...\n---')

    def stop_queue(self, tg_user_id_a, tg_user_id_b, time_stemp, session_id, bot_message):
        for user_in_queue in self.current_queue[:]:
            if ((user_in_queue['tg_user_id'] == tg_user_id_a) or 
                (user_in_queue['tg_user_id'] == tg_user_id_b)):
                self.db.Stop_queue(user_in_queue['queue_id'], time_stemp, session_id)
                
                self.send(user_in_queue['tg_user_id'], bot_message)

                self.current_queue.remove(user_in_queue)

    def stop_session(self, tg_user_id, time_stemp, status, bot_message):
        for session in self.current_sessions[:]:
            if (session['tg_user_id_a'] == tg_user_id or
                session['tg_user_id_b'] == tg_user_id ):
                self.db.Stop_session(session['session_id'], time_stemp, status)
                
                self.send(session['tg_user_id_a'], bot_message)
                self.send(session['tg_user_id_b'], bot_message)

                self.current_sessions.remove(session)
