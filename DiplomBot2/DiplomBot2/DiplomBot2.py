import requests
import webbrowser
import telegram
import subprocess
import re
import os
import paramiko
import psutil
import pycaw.pycaw
import random
import requests
from pycaw.pycaw import AudioUtilities
from pathlib import Path 
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

# ТОКЕН ID
def is_valid_user(user_id, filename):
    try:
        with open(filename) as file:
            # просмотр файла
            allowed_ids = set(int(line.strip()) for line in file)
    except FileNotFoundError:
        # создание файла, если он не существует
        with open(filename, 'w') as file:
            allowed_ids = set()
    # проверка, является ли пользователь допустимым
    return user_id in allowed_ids
def read_token(filename):
    if os.path.isfile(filename):
        # считываение токена, если файл существует
        with open(filename, 'r') as file:
            return file.readline().strip()
    else:
        # если токен не существует, запрос токена у пользователя
        print(f"Файл {filename} не найден. Создаю новый файл.")
        with open(filename, 'w') as file:
            token = input("Введите токен бота: ")
            file.write(token)
            return token


# /START
def start(update, context):
    # Получение id
    user_id = update.effective_user.id
    # Проверерка id
    if not is_valid_user(user_id, 'user.txt'):
        context.bot.send_message(chat_id=update.effective_chat.id, text='У вас нет прав на использование бота')
        return

    main_keyboard = [
        [InlineKeyboardButton("Добавить машину", callback_data='add_car_callback')],
        [InlineKeyboardButton("Все машины", callback_data='all_cars')],
    ]
    # Создание объекта клавиатуры и отправка сообщения с клавиатурой пользователю
    main_markup = InlineKeyboardMarkup(main_keyboard)
    update.message.reply_text('Выберите действие:', reply_markup=main_markup)

    # создание клавиатуры с кнопками
#    keyboard = [
#        [InlineKeyboardButton("Выключение и перезагрузка компьютера", callback_data='shut_rest')],
#        [InlineKeyboardButton("Скриншот", callback_data='screenshot')],
#        [InlineKeyboardButton("Сканирование антивируса", callback_data='scan_menu')],
#        [InlineKeyboardButton("Управление файлами", callback_data='file_menu')],
#        [InlineKeyboardButton("Проверка нагрузки на компьютер", callback_data='load_menu')],
#        [InlineKeyboardButton("Приложения", callback_data='app')],
#        [InlineKeyboardButton("Управление звуком", callback_data='sound_menu')],
#    ]
    # содаем объект клавиатуры и отправляем сообщение с клавиатурой пользователю
#    reply_markup = InlineKeyboardMarkup(keyboard)
#    update.message.reply_text('Добро пожаловать в мое меню! Что вы хотите сделать?', reply_markup=reply_markup)
# ОБРАБОТКА НАЖАТИЙ
def button_handler(update, context):
    query = update.callback_query
    action = query.data
    if action == 'add_car_callback':
    # Отправляем запрос на ввод данных (IP-адрес, хостнейм, пароль)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Введите IP-адрес, хостнейм и пароль машины в формате: IP@hostname@password')
# ВЫКЛ КОМПЬЮТЕРА
    if action == 'shut_rest':
        keyboard = [
            [InlineKeyboardButton("Выключить компьютер", callback_data='shutdown')],
            [InlineKeyboardButton("Перезагрузить компьютер", callback_data='restart')],
            [InlineKeyboardButton("Назад", callback_data='exit')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.answer(text='Выберите действие:')
        query.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    if action == 'shutdown':
        subprocess.run('shutdown /s /t 1')
        query.answer(text='Компьютер будет выключен через 1 секунду.')
    if action == 'restart':
        subprocess.run('shutdown /r /t 1')
        query.answer(text='Компьютер будет перезагружен через 1 секунду.')
# СКРИНШОТ
    if action == 'screenshot':       
        subprocess.run(['powershell', '-command', 'Add-Type -AssemblyName System.Windows.Forms; [Windows.Forms.SendKeys]::SendWait("{PRTSC}"); $image = [Windows.Forms.Clipboard]::GetImage(); $image.Save("screenshot.png")'], shell=True)
        with open('screenshot.png', 'rb') as f:
             context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)
# ПРОВЕРКА НАГРУЗКИ
    if action == 'load_menu':
        keyboard = [
            [InlineKeyboardButton("Нагрузка на ЦП", callback_data='load_cp')],
            [InlineKeyboardButton("Нагрузка на ОЗУ", callback_data='load_ram')],
            [InlineKeyboardButton("Нагрузка на Видеокарту", callback_data='load_gpu')],
            [InlineKeyboardButton("Назад", callback_data='exit')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.answer(text='Выберите действие:')
        query.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    if action == 'load_cp':
        cpu_usage = psutil.cpu_percent()  # определяет процент использования на текущий момент 
        high_cpu_texts = ["Ой, что-то я начинаю потеть... ЦП загружен на {cpu_usage}%! Может мне пора в холодильник?❄️",
                      "Кажется, мой процессор работает на полную мощность! ЦП загружен на {cpu_usage}%! 🚀", 
                      "Кто-то сказал 'горячо'? У меня процессор загружен на {cpu_usage}%! 🔥"]
        medium_cpu_texts = ["ЦП загружен на {cpu_usage}%... Надеюсь, он не подыхает от усталости! 💤", 
                        "Я вижу, что мой процессор работает на пределе... ЦП загружен на {cpu_usage}%! 💻", 
                        "Как же трудно быть ботом в эпоху цифровых технологий! ЦП загружен на {cpu_usage}%! 🤖"]
        low_cpu_texts = ["ЦП загружен на {cpu_usage}%. Может, пора уже заняться чем-нибудь более интересным? 🤔",
                     "Мой процессор работает, но не слишком усердно... ЦП загружен на {cpu_usage}%. 🤨",
                     "ЦП загружен на {cpu_usage}%. Но не переживайте, я все еще здесь и готов к работе! 😉"]
        # отправка текста при определенных условиях с рандомным сообщением
        if cpu_usage >= 70:
            text = random.choice(high_cpu_texts).format(cpu_usage=cpu_usage)
        if cpu_usage >= 50:
            text = random.choice(medium_cpu_texts).format(cpu_usage=cpu_usage)
        else:
            text = random.choice(low_cpu_texts).format(cpu_usage=cpu_usage)
        query.answer(text=text, show_alert=True)
    if action == 'load_ram':
        memory_usage = psutil.virtual_memory().percent  # определяет процент использования на текущий момент
        high_ram_texts = ["Ой, вы взорвали мою голову! 💥 ОЗУ загружен на {memory_usage}%!", 
                         "Сколько же информации вы пытаетесь загрузить? 😱 ОЗУ уже на {memory_usage}%!", 
                         "Я чувствую, что мой мозг перегружен. 🤯 ОЗУ загружен на {memory_usage}%!"]
        medium_ram_texts = ["ОЗУ загружен на {memory_usage}%... Я не уверен, что могу обработать все эти данные 🤔", 
                            "ОЗУ загружен на {memory_usage}%... Может, лучше всего мне взять перерыв? 😴", 
                            "ОЗУ загружен на {memory_usage}%... Мне нужно больше кофе! ☕"]
        low_ram_texts = ["ОЗУ загружен на {memory_usage}%. Как же здесь уютно и спокойно! 🥰", 
                        "ОЗУ загружен на {memory_usage}%. Я чувствую, себя очень хорошо! 👍", 
                        "ОЗУ загружен на {memory_usage}%. Мне все нравится! 🚀"]
        # отправка текста при определенных условиях с рандомным сообщением
        if memory_usage >= 70:
            text = random.choice(high_ram_texts).format(memory_usage=memory_usage)
        if memory_usage >= 60:
            text = random.choice(medium_ram_texts).format(memory_usage=memory_usage)
        else:
            text = random.choice(low_ram_texts).format(memory_usage=memory_usage)
        query.answer(text=text, show_alert=True)    
    if action == 'load_gpu':
        try:
            #  извлекает процент использования видеокарты
            output = os.popen('nvidia-smi --query-gpu=utilization.gpu --format=csv').readlines() 
            gpu_usage = int(output[1].split(',')[0].strip().replace('%', ''))
        except Exception as e:
            # не найдена видеокарта
            print(f"Ошибка при использовании графического процессора: {e}")
            gpu_usage = 0
            
        high_gpu_texts = ["😱 Ого! Моя видеокарта готова взорваться! Загруженность видеокарты: {gpu_usage}%!", 
                         "🤯 Видеокарта загружена на {gpu_usage}%! Не могу поверить, что она всё еще работает!", 
                         "🔥 Моя видеокарта работает на пределе! Загруженность: {gpu_usage}%!"]
        medium_gpu_texts = ["🤔 Загруженность видеокарты: {gpu_usage}%... Мне кажется, её начинает тормозить", 
                         "🤨 Видеокарта работает на полную мощность! Загруженность: {gpu_usage}%... Надеюсь, я справлюсь", 
                         "😕 Загруженность видеокарты уже {gpu_usage}%... Может, стоит переключиться на другую задачу?"]
        low_gpu_texts = ["😃 Загруженность видеокарты: {gpu_usage}%. Всё идеально! 😎", 
                         "🙂 Видеокарта работает на {gpu_usage}%. Я готов к новым вызовам! 💪", 
                         "😉 Моя видеокарта готова к работе! Загруженность всего лишь {gpu_usage}% 😉"]
        # отправка текста при определенных условиях с рандомным сообщением
        if gpu_usage >= 70:
            text = random.choice(high_gpu_texts).format(gpu_usage=gpu_usage)
        if gpu_usage >= 50:
            text = random.choice(medium_gpu_texts).format(gpu_usage=gpu_usage)
        else:
            text = random.choice(low_gpu_texts).format(gpu_usage=gpu_usage)
        query.answer(text=text, show_alert=True)
# ФАЙЛОВОЕ МЕНЮ
    if action == 'file_menu':
        keyboard = [
            [InlineKeyboardButton("Сохранить файл", callback_data='save_file')],
            [InlineKeyboardButton("Отправить файл", callback_data='send_file')],
            [InlineKeyboardButton("Назад", callback_data='exit')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.answer(text='Выберите действие:')
        query.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    if action == 'save_file':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Нажатие на эту кнопку является необязательным, так как вы можете просто отправить мне файл и указать его название в подписи. \n\nЕсли вы не укажете название файла, я сохраню его с помощью уникального идентификатора сообщения.')
    if action == 'send_file':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Пожалуйста, укажите название файла, например 849.docx, который нужно отправить. Если файл находится на рабочем столе, укажите это.\n\nАльтернативно, вы можете указать путь к файлу или каталогу, где находятся нужные файлы. Например: /d D://231/...\n\n И я передам вам файлы.')
# АНТИВИРУС
    if action == 'scan_menu':
        keyboard = [
            [InlineKeyboardButton("Быстрое сканирование", callback_data='fast_scan')],
            [InlineKeyboardButton("Полное сканирование", callback_data='full_scan')],
            [InlineKeyboardButton("Включить - Выключить антивирусник", callback_data='off_on')],
            [InlineKeyboardButton("Назад", callback_data='exit')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.answer(text='Выберите тип сканирования:')
        query.message.reply_text('Выберите тип сканирования:', reply_markup=reply_markup)
    if action == 'fast_scan':
        # старт быстрого сканирования
        query.edit_message_text(text='Происходит быстрое сканирование...')
        result = subprocess.run('C:\\Program Files\\Windows Defender\\MpCmdRun.exe -Scan -ScanType 1', capture_output=True, text=True)
        # если ошибка 
        if "No threats found" in result.stdout:
            query.edit_message_text(text='Ошибка при сканирование.')
        else:
            #результаты угроз
            threats = re.findall(r'ThreatCount\s+:\s+(\d+)', result.stdout)
            # если есть
            if threats:
                query.edit_message_text(text=f'Быстрое сканирование завершено. Обнаружено угроз: {threats[0]}')
            else:
                #если нет
                query.edit_message_text(text='Быстрое сканирование завершено. Угроз не обнаружено.')
    if action == 'full_scan':
        # старт полного сканирования
        query.edit_message_text(text='Происходит полное сканирование...')
        result = subprocess.run('C:\\Program Files\\Windows Defender\\MpCmdRun.exe -Scan -ScanType 2', capture_output=True, text=True)
        # если ошибка 
        if "No threats found" in result.stdout:
            query.edit_message_text(text='Полное сканирование завершено. Угроз не обнаружено.')
        else:
            #результаты угроз
            threats = re.findall(r'ThreatCount\s+:\s+(\d+)', result.stdout)
            if threats:
            # если есть
                query.edit_message_text(text=f'Полное сканирование завершено. Обнаружено угроз: {threats[0]}')
            else:
            #если нет
                query.edit_message_text(text='Полное сканирование завершено. Угроз не обнаружено.')
# ЗВУК
    if action == 'sound_menu':
        keyboard = [
            [InlineKeyboardButton("Громче", callback_data='increase_volume')],
            [InlineKeyboardButton("Тише", callback_data='decrease_volume')],
            [InlineKeyboardButton("Назад", callback_data='exit')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.answer(text='Выберите действие:')
        query.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    if action == "increase_volume":
        import comtypes
        comtypes.CoInitialize()
        # получение всех сессий
        sessions = AudioUtilities.GetAllSessions()
        # проход по сессиям и увелечение громкости
        for session in sessions:
            volume = session._ctl.QueryInterface(pycaw.pycaw.ISimpleAudioVolume)
            current_volume = volume.GetMasterVolume()
            new_volume = min(current_volume + 0.25, 1.0)
            volume.SetMasterVolume(new_volume, None)
            # сообщение в чат с новым значением громкости
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Громкость увеличена до {int(new_volume * 100)}%.')
    if action == "decrease_volume":
        import comtypes
        comtypes.CoInitialize()
                # получение всех сессий
        sessions = AudioUtilities.GetAllSessions()
        # проход по сессиям и увелечение громкости
        for session in sessions:
            volume = session._ctl.QueryInterface(pycaw.pycaw.ISimpleAudioVolume)
            current_volume = volume.GetMasterVolume()
            new_volume = max(current_volume - 0.25, 0.0)
            volume.SetMasterVolume(new_volume, None) 
            # сообщение в чат с новым значением громкости
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Громкость уменьшена до {int(new_volume * 100)}%.')
    if action == 'exit':
        query.delete_message()
 # ПРИЛОЖЕНИЕ  
    if action == 'app':
        keyboard = [
            [InlineKeyboardButton("Все приложения", callback_data='apps')],
            [InlineKeyboardButton("Добавить приложение", callback_data='app_new')],
            [InlineKeyboardButton("Назад", callback_data='exit')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.answer(text='Выберите действие:')
        query.message.reply_text('Выберите действие:', reply_markup=reply_markup)
    if action == 'apps':
        display_apps(update, context) # перенаправление
    if action == 'app_new':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Чтобы сохранить приложение и добавить его в список всех приложений, напишите команду: \n\"/s Имя приложения -- Путь к приложению".')
# СОХРАНЕНИЕ ФАЙЛА
def handle_document(update, context):
    # Получаем объект файла из сообщения
    file = context.bot.get_file(update.message.document.file_id)
    # Получаем расширение файла и имя файла из сообщения
    file_extension = Path(update.message.document.file_name).suffix
    file_name = update.message.caption
    # Если имя файла не указано, формируем его из ID сообщения и расширения файла
    if not file_name:
        file_name = f"{update.message.message_id}{file_extension}"
    else:
        file_name += file_extension
    # Формируем путь к файлу на рабочем столе
    file_path = f"C:/Users/Максим/Desktop/{file_name}"
    # Скачиваем файл по заданному пути
    file.download(custom_path=file_path)
    # Отправляем сообщение в чат с указанием имени сохраненного файла
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Файл {file_name} сохранен на рабочем столе.')
# ОТПРАВКА ФАЙЛА
def file(update, context):
    # Проверяем, содержит ли сообщение команду для отправки файлов из директории
    if "/d" in update.message.text:
        # Извлекаем путь к директории из сообщения пользователя
        directory_path = update.message.text.replace("/d", "").strip()
        # Проверяем, является ли указанный путь директорией
        if not os.path.isdir(directory_path):
            update.message.reply_text("<b>Ошибка:</b> Указанный путь не является директорией.", parse_mode=ParseMode.HTML)
            return
        # Получаем список файлов в директории
        files = os.listdir(directory_path)
        # Формируем сообщение с содержимым директории
        message = f"<b>Содержимое директории:</b> <code>{directory_path}</code>\n\n"
        for file in files:
            # Проверяем, является ли файл обычным файлом
            if os.path.isfile(os.path.join(directory_path, file)):
                # Отправляем файл как документ, если это не файл изображения
                if not (file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png') or file.endswith('.gif')):
                    try:
                        with open(os.path.join(directory_path, file), 'rb') as f:
                            context.bot.send_document(chat_id=update.effective_chat.id, document=f)
                    except Exception as e:
                        pass
                else:
                    # Отправляем файл как фото, если это файл изображения
                    with open(os.path.join(directory_path, file), 'rb') as f:
                        context.bot.send_photo(chat_id=update.effective_chat.id, photo=f)
            # Проверяем, есть ли файлы в директории
            elif os.path.isdir(os.path.join(directory_path, file)):
                message += f"📁 <code>{file}</code>\n"
        # Отправляем сообщение с содержимым директории в чат
        update.message.reply_text(message, parse_mode=ParseMode.HTML)
    else:
        # Получаем путь к файлу из сообщения пользователя
        file_path = update.message.text.strip()
        # Проверяем, существует ли файл по указанному пути
        if not os.path.exists(file_path):
            # Если файл не найден, формируем путь к файлу на рабочем столе
            file_path = os.path.join(os.path.expanduser("~"), "Desktop", file_path)
        # Проверяем, существует ли файл по новому пути
        if os.path.exists(file_path):
            # Отправляем файл как документ в чат
            context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_path, 'rb'))
        else:
            # Если файл не найден, отправляем сообщение об ошибке
            update.message.reply_text(f'Файл "{file_path}" не найден на вашем компьютере.')
# ОТКРЫТИЕ ССЫЛОК
def url(update, context):
    message = update.message.text
    # Используем регулярное выражение, чтобы найти ссылку в сообщении пользователя
    regex = r"(?P<url>https?://[^\s]+)"
    match = re.search(regex, message)

    if match:
        url = match.group("url")
        # Отправляем GET-запрос по указанной ссылке
        response = requests.get(url)
        # Проверяем, что запрос успешен (код ответа 200)
        if response.status_code == 200:
            # Открываем ссылку в браузере
            webbrowser.open(url)
            update.message.reply_text(f"Открываю ссылку {url} в браузере.")
        else:
            update.message.reply_text(f"Не удалось открыть ссылку {url}. Код ответа: {response.status_code}")
    else:
        update.message.reply_text("В сообщении не найдено ссылок.")
# ЗАПУСК ПРИЛОЖЕНИЙ
def handle_command(update, context):
    command = update.message.text
    # Проверяем, что команда начинается с символа "/p"
    if command.startswith('/p '):
        # Извлекаем путь к приложению из команды пользователя
        app_path = command[3:]
        try:
            # Вызываем функцию запуска приложения
            completed_process = subprocess.run(app_path, shell=True, capture_output=True)
            if completed_process.returncode == 0:
                message = f"Программа '{app_path}' успешно запущена."
            else:
                error_message = completed_process.stderr.decode('utf-8').strip()
                message = f"Ошибка при запуске программы '{app_path}': {error_message}"
        except Exception as e:
            message = f"Произошла ошибка при запуске программы '{app_path}': {str(e)}"
        # Отправляем пользователю сообщение о результате запуска приложения
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
# СОХРАНЕНИЕ ИМЕНИ И ПУТИ
def save_app_path(update, context):
    args = context.args
    if len(args) < 2:
        # при вводе не правильного формата
        context.bot.send_message(chat_id=update.effective_chat.id, text='Ошибка: неверный формат команды. Используйте /s ИмяПриложения ПутьКПриложению')
        return
    app_name = args[0]
    app_path = args[1]
    # путь сохранения
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, "app_paths.txt")
    # проверка сохранения проложения
    with open(file_path, "a") as f:
        f.write(f"{app_name} -- {app_path}\n")
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Путь к приложению '{app_name}' успешно сохранен.")
 # КЛАВ С ПРИЛОЖЕНИЯМИ
def display_apps(update, context):
    # Открываем файл с сохраненными путями
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_path = os.path.join(desktop_path, "app_paths.txt")
    with open(file_path, "r") as f:
        app_paths = f.readlines()
    # Создаем список кнопок
    buttons = []
    for path in app_paths:
        app_name, app_path = path.strip().split(" -- ")
        button = InlineKeyboardButton(text=app_name, callback_data=f"run_app_{app_path}")
        buttons.append([button])
    # Создаем разметку для кнопок
    reply_markup = InlineKeyboardMarkup(buttons)
    # Отправляем пользователю сообщение с меню
    context.bot.send_message(chat_id=update.effective_chat.id, text="Выберите приложение:", reply_markup=reply_markup)
 # ЗАПУСК ЧЕРЕЗ КЛАВ
def run_app(update, context):
        # Получаем путь к приложению
    app_path = '"' + update.callback_query.data.replace("run_app_", "") + '"'
    # Запускаем приложение
    subprocess.run(app_path, shell=True)
# МОНИТОРИНГ
def check_cpu_load(context):
    chat_id = '574340191'
    cpu_load = psutil.cpu_percent()  # сканирование нагрузки
    # при нагрузке больше 50 отправка сообщения в чат
    if cpu_load > 50:
        context.bot.send_message(chat_id=chat_id, text=f'Высокая нагрузка на процессор: {cpu_load}%')
    ram_load = psutil.virtual_memory().percent
    if ram_load > 50:
        context.bot.send_message(chat_id=chat_id, text=f'Высокая нагрузка на ОЗУ: {ram_load}%')
def check_gpu_load(context):
    chat_id = '574340191'
    gpu_load = os.popen('nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits').read().strip()  # сканирование нагрузки
    gpu_load = int(gpu_load)
    # при нагрузке больше 50 отправка в чат
    if gpu_load > 50:
        context.bot.send_message(chat_id=chat_id, text=f'Высокая нагрузка на видеокарту: {gpu_load}%')
# HELP
def help(update, context):
    help_message = """
    СПИСОК ФУНКЦИЙ ДЛЯ КЛАВИАТУРЫ, ЧТО ЗА ЧТО ОТВЕЧАЕТ:

    "Выключение и перезагрузка компьютера" - кнопка, при нажатии на которую можно выполнить выключение или перезагрузка компьютера.

    "Скриншот" - кнопка, при нажатии на которую делается скриншот экрана компьютера.

    "Сканирование антивируса" - кнопка, при нажатии на которую можно запустить сканирование компьютера на наличие вредоносного программного обеспечения. Можно выполнить полную и быструю проверку.

    "Управление файлами" - кнопка, при нажатии на которую открывается меню управления файлами на компьютере.

    "Проверка нагрузки на компьютер" - кнопка, при нажатии на которую можно выполнить проверку текущей нагрузки на компьютер.

    "Приложения" - кнопка, при нажатии на которую открывается можно добавлять приложения для запуска.

    "Управление звуком" - кнопка, при нажатии на которую открывается меню управления звуком на компьютере.

    СПИСОК ДОСТУПНЫХ КОММАНД:
    
    /start - Открывает главную клавиатуру.
    
    /d - Позволяет отправлять файлы. Просто укажите название файла, который нужно отправить. Если файл находится на рабочем столе, то его можно отправить, указав только его название. Если файл находится в другом месте на компьютере, вам необходимо указать путь к файлу или каталогу, где находятся нужные файлы. Например: "/d D://231/...". После этого бот передаст вам запрошенные файлы.
    
    /u - Открывает указанный вами сайт на вашем компьютере. Для этого введите команду /u и укажите ссылку на сайт. Например, "/u https://www.google.com".
    
    /p - Запускает приложение, указанное вами. Просто введите команду /p и укажите путь к файлу, например: "/p D://ddee/edf/...". Бот запустит приложение для вас. Это удобно, если вы часто используете новые или временные приложения, которые не хотите сохранять в базе данных.
    
    /s - Позволяет сохранять приложения в базе данных бота. Для сохранения приложения необходимо отправить команду "/s Имя приложения Путь к приложению", где "Имя приложения" - это название приложения, а "Путь к приложению" - это путь к файлу приложения на устройстве пользователя. 

    Кроме того, вы можете сохранять файлы, отправляя их боту. Вы можете указать, как именно сохранить файл, написав комментарий к сообщению с файлом. Если вы не указываете никакой комментарий, то бот автоматически сохраняет файл по уникальному идентификатору.
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)

def process_user_input(update, context):
    # Получаем введенный пользователем текст
    user_input = update.message.text

    # Разделяем введенные данные на IP-адрес, хостнейм и пароль
    car_data = user_input.split('@')
    if len(car_data) != 3:
        # Если количество элементов не равно 3, значит формат ввода неверный
        context.bot.send_message(chat_id=update.effective_chat.id, text='Неверный формат ввода. Пожалуйста, введите IP-адрес, хостнейм и пароль машины в формате: IP@hostname@password')
        return

    # Извлекаем IP-адрес, хостнейм и пароль из разделенных данных
    car_ip = car_data[0].strip()
    car_hostname = car_data[1].strip()
    car_password = car_data[2].strip()

    # Пробуем подключиться к машине по SSH
    try:
        # Создаем SSH-клиент
        ssh_client = paramiko.SSHClient()

        # Устанавливаем политику автоматического добавления хоста в список известных хостов
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Подключаемся к машине
        ssh_client.connect(car_ip, username='root', password=car_password)

        # Закрываем SSH-соединение
        ssh_client.close()

        # Сохраняем данные машины
        context.user_data['car_ip'] = car_ip
        context.user_data['car_hostname'] = car_hostname
        context.user_data['car_password'] = car_password

        # Отправляем сообщение с подтверждением
        confirmation_message = f'Машина успешно добавлена!\nIP-адрес: {car_ip}\nХостнейм: {car_hostname}\nПароль: {car_password}'
        context.bot.send_message(chat_id=update.effective_chat.id, text=confirmation_message)
    except paramiko.AuthenticationException:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Ошибка аутентификации. Пожалуйста, проверьте правильность пароля.')
    except paramiko.SSHException as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Ошибка подключения по SSH: {str(e)}')
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Произошла ошибка: {str(e)}')


# ТОКЕН И ОБНОВЛЕНИЯ
updater = Updater(read_token("tok.txt"), use_context=True)  # создает экземпляр класса Updater, используя токен бота, который считывается из файла "tok.txt"
dispatcher = updater.dispatcher                                #  создает диспетчер для обработки входящих сообщений.
updater.job_queue.run_repeating(check_cpu_load, interval=3600, first=0)     # запускает регулярную задачу на проверку загрузки процессора с интервалом в 1 час
updater.job_queue.run_repeating(check_gpu_load, interval=3600, first=0)     # запускает регулярную задачу на проверку загрузки видеокарты с интервалом в 1 час
updater.dispatcher.add_handler(CallbackQueryHandler(run_app, pattern=r"^run_app"))   # добавляет обработчик колбэк-запросов, используя функцию run_app


# ОБРАБОТЧИКИ ФУНКЦИЙ
dispatcher.add_handler(CommandHandler('start', start))  # добавляет обработчик команды /start, который вызывает функцию start
dispatcher.add_handler(CallbackQueryHandler(button_handler))  # добавляет обработчик для инлайн-кнопок, который вызывает функцию button_handler.
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, file))  # добавляет обработчик текстовых сообщений, которые не являются командами, и вызывает функцию file
dispatcher.add_handler(MessageHandler(Filters.document, handle_document))    # добавляет обработчик документов, и вызывает функцию handle_document
dispatcher.add_handler(CommandHandler("d", file))   #  добавляет обработчик команды /d, и вызывает функцию file
dispatcher.add_handler(CommandHandler("u", url))     # добавляет обработчик команды /u, и вызывает функцию url
dispatcher.add_handler(CommandHandler("s", save_app_path))  # добавляет обработчик команды /s, и вызывает функцию save_app_path
dispatcher.add_handler(CommandHandler("p", handle_command))    # добавляет обработчик команды /p, и вызывает функцию handle_command
dispatcher.add_handler(CommandHandler("help", help))           # добавляет обработчик команды /help, и вызывает функцию help
dispatcher.add_handler(CommandHandler("ssh", process_user_input))   
# ЗАПУСК БОТА
updater.start_polling()   # запуск бота, при котором бот постоянно опрашивает сервер Telegram на наличие новых сообщений и обновлений
updater.idle()          # остановка бота после получения сигнала прерывания