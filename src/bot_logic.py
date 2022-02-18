import schedule, time, random
from libs.models.nickname_generator import generate_nickname
# from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


class Bot_logic:

    MIN_WAITING_IN_QUEUE = 3
    MAX_WAITING_IN_QUEUE = 180
    
    MAX_WAITING_IN_SESSIONS = 30

    COMPANION_TIME_OUT = 30 
    # Предел времи ожидания в очереди, для прошлого собеседника 
    # (если только они в двоем в очереди, через это время соеденит)
    # MIN_WAITING_IN_QUEUE < it < MAX_WAITING_IN_QUEUE

    BONUS_SELECT_BOT_MESSAGE = 10
    BONUS_SELECT_NOT_BOT_MESSAGE = -5 # all in session

    BONUS_NOT_SELECT_BOT_MESSAGE = -10
    BONUS_NOT_SELECT_NOT_BOT_MESSAGE = 0

    BUYING_REPLACE_NAME = 100

    bot_send = None # def send(tg_user_id, send_message)
    delete = None # def send(tg_user_id, message_id)
    answer = None
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
            'test': self.cmd_test,
            'top': self.cmd_top
        }

    # handlers

    def handler_commands(self, command_name, tg_user_id, message_id):
        self.delete_wait_clear_cmd(tg_user_id)

        self.commands[command_name](tg_user_id)

        self.wait_clear_cmd[tg_user_id] = message_id


    impudence = [] # [{'session_id': 0, 'message_id': 0, 'arr': []}]
    is_bot = [] # [{'session_id': 0, 'tg_user_id': 0, 'message_id': 0, 'text': "", 'time_send': 0}]

    def handler_message(self, tg_user_id, message):

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
            send_message = self.modify_msg.preprocess(message)
            answer = self.modify_msg.answering_machine(send_message)
            if answer != 0:
                self.db.Add_log(tg_user_id, session_id, message, time_send, "original", 0)
                self.send_and_bot_button(session_id, tg_user_id_companion, tg_user_id, answer, time_send)
                self.send(tg_user_id_companion, '> Он такой: ' +  send_message + '\n\n> А я такой: ' + answer, clear=True)
            else:
                self.send_and_bot_button(session_id, tg_user_id, tg_user_id_companion, send_message, time_send)
            
                user_id = self.db.Get_id_from_tg_user_id(tg_user_id)
                debug_msg = self.modify_msg.dialogue_analysis(self.db.Get_data_fro_analysis(), user_id, session_id, self.db.Get_count_message_in_session(session_id), send_message)
                self.send(tg_user_id, debug_msg, clear=True)
                # self.send(tg_user_id, self.modify_msg.preprocess(message), parse_mode='Markdown')
                self.db.Add_log(tg_user_id, session_id, message, time_send, "original", 0)

                impudence = self.modify_msg.impudence(message, self.db.Get_count_message_in_session(session_id))
                if impudence:
                
                    msg_for_select = f""
                    for k, v in enumerate(impudence):
                        msg_for_select += f"\n{k+1} - " + v
                    msg_for_select += f""

                    self.delete_wait_clear_cmd(tg_user_id)
                    self.delete_wait_clear_msg(tg_user_id)

                    msg = self.send( tg_user_id_companion, msg_for_select, reply_markup = self.create_buttons(['1','2','3'], "impudence"))
                    self.impudence.append({'session_id': session_id, 'message_id': msg.message_id, 'arr': impudence})
        else:
            self.send(tg_user_id, "> /info", clear=True)
            # self.send(tg_user_id,  self.modify_msg.process(message), parse_mode='Markdown')
            # self.send(tg_user_id,  self.modify_msg.fuckoff(), parse_mode='Markdown')
    
    def handler_button(self, tg_user_id, data, message_id, call_id):
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
            selected_id = int(data[0])

            if data[1] == 'impudence':
                impud = {}
                for v in self.impudence[:]:
                    if v['message_id'] == message_id:
                        impud = v
                        break
                
                self.delete(tg_user_id, impud['message_id'])
                impudence_msg = impud['arr'][selected_id]
                self.send(tg_user_id, f"> Вы отправили:\n> {impudence_msg}")

                self.send_and_bot_button(session_id, tg_user_id, tg_user_id_companion, impudence_msg, time_send)

                self.db.Add_log(tg_user_id, session_id, impudence_msg, time_send, "from_bot", 0)
                log_id = self.db.Get_log_id_session_id_and_time_send(session_id, time_send)
                self.db.Add_selectors(log_id, selected_id, impud['arr'])

                self.impudence.remove(impud)

            if data[1] == 'is_bot':
                self.remove_button_bot_from_last_mgs(tg_user_id, tg_user_id_companion,  1, message_id, call_id)

        if data[1] == "buying_replace_name":
            added_points = self.db.Get_all_users_points_from_interval(0, time_send)
            user_id = self.db.Get_id_from_tg_user_id(tg_user_id)
            if added_points[user_id] >= self.BUYING_REPLACE_NAME:
                self.db.Add_points(tg_user_id, -self.BUYING_REPLACE_NAME, time_send)
                self.answer(call_id, f"> -{self.BUYING_REPLACE_NAME} очков", cache_time=60)
                pseudonym = ""
                while True:
                    pseudonym = generate_nickname()
                    finded_users = self.db.Get_user_id_from_pseudonym(pseudonym)
                    if finded_users == None:
                        break

                self.db.Change_pseudonym(user_id, pseudonym)
                self.delete(tg_user_id, message_id)
                self.send(tg_user_id, f"> Ваш новый псевдоним:\n- {pseudonym}", clear=True)
                #self.cmd_top(tg_user_id)
            else:
                self.answer(call_id, f"> Недостаточно очков", cache_time=60)

        if data[1] == "/start":
            self.cmd_start(tg_user_id)

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
                self.stop_queue(tg_user_id, tg_user_id, time_stemp, "NULL", '> Превышено время ожидания в очереди. /start', clear = True)

        for session in self.current_sessions:
            last_message_timestamp = self.db.Get_last_message_timestamp_from_session_id(session['session_id'])
            if not last_message_timestamp:
                last_message_timestamp = session['time_start']
            waiting_time = time_stemp - last_message_timestamp
            if waiting_time > self.MAX_WAITING_IN_QUEUE:
                tg_user_id = session['tg_user_id_a']
                self.stop_session(tg_user_id, time_stemp, f"Timeout({self.MAX_WAITING_IN_SESSIONS})", '> Превышено время ожидания в сессии. /start')

    # commands

    def cmd_start(self, tg_user_id):
        time_stemp = int(time.time()*1000)/1000
        if not self.db.Get_id_from_tg_user_id(tg_user_id):

            pseudonym = ""
            while True:
                pseudonym = generate_nickname()
                finded_users = self.db.Get_user_id_from_pseudonym(pseudonym)
                if finded_users == None:
                    break
            self.db.Add_user(tg_user_id, 0, pseudonym)

            self.send(tg_user_id,f"Добро пожаловать!\n\nВаш уникальный псевдоним:\n{pseudonym}\n\nНачать - /start\nБольше инофрмации - /info")
            self.db.Add_points(tg_user_id, 0, time_stemp)
            time.sleep(1)

        self.add_to_queue(tg_user_id, time_stemp)

    def cmd_stop(self, tg_user_id):
        time_stemp = int(time.time()*1000)/1000
        self.stop_queue(tg_user_id, tg_user_id, time_stemp, "NULL", '> Поиск остановлен. /start', clear = True)
        self.stop_session(tg_user_id, time_stemp, "command_stop", '> Сессия остановлена. /start')

    def cmd_info(self, tg_user_id):
        msg = f"Начать - /start\nОстановить - /stop\nТоп - /top\nБольше информации - /info\n\n"
        msg += f"Правила: (...)\n\n"
        msg += self.get_msg_online()
        self.send(tg_user_id, msg, clear = True)

    def cmd_test(self, tg_user_id):
        self.modify_msg.flag = True

    def cmd_test(self, tg_user_id):
        self.modify_msg.flag = True

    def cmd_top(self, tg_user_id):
        res = self.db.Get_all_users_points_from_interval(0, time.time())

        sys_msg = ""
        sys_msg += f"> Топ пользователей:\n\n"

        top_count = 10
        i = 1
        for k, v in sorted(res.items(), key=lambda item: item[1], reverse=True):
            pseudonym = self.db.Get_pseudonym_from_user_id(k)
            sys_msg += f"{i} - {pseudonym} - {v}\n"

            if i == top_count: 
                break
            i += 1
        
        user_id = self.db.Get_id_from_tg_user_id(tg_user_id)
        pseudonym = self.db.Get_pseudonym_from_user_id(user_id)
        points = res[int(user_id)]

        sys_msg += f"\nВаш псевдоним:\n- {pseudonym}\nВаши очки: {points}\n"

        self.send(tg_user_id, sys_msg, reply_markup = self.create_buttons([f'🔄 Новый псевдоним - {self.BUYING_REPLACE_NAME} очков'], "buying_replace_name"), clear=True)

    # utils

    def send_and_bot_button(self, session_id, tg_user_id, tg_user_id_companion, send_message, time_send):
        self.remove_button_bot_from_last_mgs(tg_user_id, tg_user_id_companion)   

        self.delete_wait_clear_cmd(tg_user_id)
        self.delete_wait_clear_msg(tg_user_id)
        
        msg = self.send(tg_user_id_companion, send_message, parse_mode='Markdown', reply_markup = self.create_buttons(['🤖'], "is_bot"))
        
        self.is_bot.append({'session_id': session_id, 'tg_user_id': tg_user_id_companion, 'message_id': msg.message_id, 'text': send_message, 'time_send': time_send})


    def remove_button_bot_from_last_mgs(self, tg_user_id, tg_user_id_companion, grade = 0, message_id = 0, call_id = 0):
        for v in self.is_bot[:]:
            if ((grade != 0 and v['message_id'] == message_id) or 
                (grade == 0 and v['tg_user_id'] == tg_user_id)):
                detected_bot = v
                
                self.edit(chat_id = tg_user_id, message_id = detected_bot['message_id'], text = detected_bot['text'])
                
                log_id = self.db.Get_log_id_session_id_and_time_send(detected_bot["session_id"], detected_bot['time_send'])

                if grade != 0:
                    
                    self.db.Change_grade(log_id, grade)

                    if self.db.Get_is_bot_from_log_id(log_id):
                        self.answer(call_id, f"это БОТ\n+{self.BONUS_SELECT_BOT_MESSAGE} очков", cache_time=120)
                        self.db.Add_points(tg_user_id, self.BONUS_SELECT_BOT_MESSAGE, detected_bot['time_send'])
                    else:
                        self.answer(call_id, f"это НЕ бот\n{self.BONUS_SELECT_NOT_BOT_MESSAGE} очков", cache_time=120)
                        self.db.Add_points(tg_user_id, self.BONUS_SELECT_NOT_BOT_MESSAGE, detected_bot['time_send'])
                        self.db.Add_points(tg_user_id_companion, self.BONUS_SELECT_NOT_BOT_MESSAGE, detected_bot['time_send'])
                else:
                    if log_id and self.db.Get_is_bot_from_log_id(log_id):
                        self.db.Add_points(tg_user_id, self.BONUS_NOT_SELECT_BOT_MESSAGE, detected_bot['time_send'])
                    #else:
                        #self.db.Add_points(tg_user_id, self.BONUS_NOT_SELECT_NOT_BOT_MESSAGE, detected_bot['time_send'])

                self.is_bot.remove(detected_bot)  

    def get_msg_online(self) -> str:
        # users_counts = len(self.db.Sql("SELECT * FROM users;"))
        queue_counts = len(self.current_queue)
        session_counts = len(self.current_sessions)*2
        return f'Онлайн пользователи:\nв очереди - {queue_counts}\nв сессиях - {session_counts}\n'

    def add_to_queue(self, tg_user_id, time_stemp):
        for user_in_queue in self.current_queue:
            if user_in_queue['tg_user_id'] == tg_user_id:
                return

        for sessions in self.current_sessions:
            if (sessions['tg_user_id_a'] == tg_user_id or
                sessions['tg_user_id_b'] == tg_user_id):
                self.send(tg_user_id, "> Вы в сессии. /stop , /start", clear=True)
                return

        msg = self.get_msg_online()
        self.send(tg_user_id, f'{msg}\n> Поиск собеседника. Пожалуйста, подождите...', clear=True) # f'Please wait at least {self.MIN_WAITING_IN_QUEUE} seconds...')

        self.db.Add_queue(tg_user_id, time_stemp)

        queue_id = self.db.Get_queue_id_from_time_start(time_stemp)
        last_companion = self.db.Get_last_companion(tg_user_id)
        self.current_queue.append({'queue_id': queue_id,'tg_user_id': tg_user_id, 'time_start': time_stemp, 'last_companion': last_companion})

    def add_to_sessions(self, tg_user_id_a, tg_user_id_b, time_stemp):
        self.db.Add_session(tg_user_id_a, tg_user_id_b, time_stemp)

        session_id = self.db.Get_session_id_from_time_start(time_stemp)
        self.current_sessions.append({'session_id': session_id, 'tg_user_id_a': tg_user_id_a, 'tg_user_id_b': tg_user_id_b, 'time_start': time_stemp})
        
        self.delete_wait_clear_cmd(tg_user_id_a)
        self.delete_wait_clear_cmd(tg_user_id_b)
        self.stop_queue(tg_user_id_a, tg_user_id_b, time_stemp, session_id, '> Собеседник найден!')

    def stop_queue(self, tg_user_id_a, tg_user_id_b, time_stemp, session_id, bot_message, clear = False):
        for user_in_queue in self.current_queue[:]:
            if ((user_in_queue['tg_user_id'] == tg_user_id_a) or 
                (user_in_queue['tg_user_id'] == tg_user_id_b)):
                self.db.Stop_queue(user_in_queue['queue_id'], time_stemp, session_id)
                
                self.send(user_in_queue['tg_user_id'], bot_message, clear=clear)

                self.current_queue.remove(user_in_queue)

    def stop_session(self, tg_user_id, time_stemp, status, bot_message):
        for session in self.current_sessions[:]:
            if (session['tg_user_id_a'] == tg_user_id or
                session['tg_user_id_b'] == tg_user_id ):
                self.db.Stop_session(session['session_id'], time_stemp, status)

                #
                self.remove_button_bot_from_last_mgs(session['tg_user_id_a'], session['tg_user_id_b'])
                self.remove_button_bot_from_last_mgs(session['tg_user_id_b'], session['tg_user_id_a'])

                added_points = self.db.Get_all_users_points_from_interval(session['time_start'], time_stemp)
                user_id_a = self.db.Get_id_from_tg_user_id(session['tg_user_id_a'])
                user_id_b = self.db.Get_id_from_tg_user_id(session['tg_user_id_b'])
                
                added_points_a = added_points[user_id_a] if added_points.get(user_id_a) else 0
                added_points_b = added_points[user_id_b] if added_points.get(user_id_b) else 0

                msg_a = bot_message + f"\nПрирост очков за сессию: {added_points_a}"
                msg_b = bot_message + f"\nПрирост очков за сессию: {added_points_b}"

                points = self.db.Get_all_users_points_from_interval(0, time_stemp)
                msg_a += f"\nВсего очков: {points[user_id_a]}"
                msg_b += f"\nВсего очков: {points[user_id_b]}"


                self.delete_wait_clear_cmd(session['tg_user_id_a'])
                self.delete_wait_clear_cmd(session['tg_user_id_b'])

                self.delete_wait_clear_msg(session['tg_user_id_a'])
                self.delete_wait_clear_msg(session['tg_user_id_b'])
                #
                
                
                #buttons = self.create_buttons(['👥 Начать заново'], "/start")
                self.send(session['tg_user_id_a'], msg_a)#, reply_markup=buttons)
                self.send(session['tg_user_id_b'], msg_b)#, reply_markup=buttons)

                self.current_sessions.remove(session)

    # buttons_info = []

    def send(self, tg_user_id, message, parse_mode=None, reply_markup=None, clear=False):
        self.delete_wait_clear_cmd(tg_user_id)
        self.delete_wait_clear_msg(tg_user_id)

        msg = self.bot_send(tg_user_id, message, parse_mode=parse_mode, reply_markup=reply_markup)
        
        # if reply_markup:
        #     self.buttons_info.append({})

        if clear:
            self.wait_clear_msg[tg_user_id] = [msg.message_id, message]

        return msg


    wait_clear_cmd = {}
    wait_clear_msg = {}

    def delete_wait_clear_cmd(self, tg_user_id):
        old_message_id = self.wait_clear_cmd.get(tg_user_id)
        if old_message_id:
            try:
                self.delete(tg_user_id, old_message_id)
            except Exception as e:
                print(f"Error: not found message_id for cmd: \n{e}")
            self.wait_clear_cmd.pop(tg_user_id)

    def delete_wait_clear_msg(self, tg_user_id):
        message_id = self.wait_clear_msg.get(tg_user_id)
        if message_id:
            try:
                self.delete(tg_user_id, message_id[0])
            except Exception as e:
                print(f"Error: not found message_id for message:\n{message_id[1]}")
            self.wait_clear_msg.pop(tg_user_id)
