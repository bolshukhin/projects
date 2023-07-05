import time
import requests
import telebot
import datetime
import schedule

# API ключи
from config import TOKEN_WHEATHER, CHAT_ID_GROUP, API_KEYS, CHAT_ID_PRIVATE

# Координаты
LATITUDE = 59.992330
LONGITUDE = 32.033880

# Инициализация бота и переменной prev_weather перед началом цикла 
bot = telebot.TeleBot(TOKEN_WHEATHER)
# Функция для отправки сообщения в телеграмм
def send_message(message):
    bot.send_message(chat_id=(CHAT_ID_GROUP), text=message)
def error_message(message_error):
    bot.send_message(chat_id=(CHAT_ID_PRIVATE), text=message_error)
prev_weather = None
def get_weather():
    global weather_condition
    global temperature
    global feels_like_temp
    global pressure_mmHg
    global humidity_percent
    global wind_speed_msec
    global weather
    
    # URL для запроса погоды 
    URL = f"https://api.weather.yandex.ru/v2/informers?lat={LATITUDE}&lon={LONGITUDE}&lang=ru_RU"
    
    HEADERS = {
        "X-Yandex-API-Key": API_KEYS[0],  # используем первый ключ из массива 
        "Accept-Language": "ru"
    }
    
    response = requests.get(URL, headers=HEADERS)
    
     # Если возникает ошибка при обращении к API Яндекс Погоды,
     # то переключаемся на следующий доступный ключ и повторяем запрос.
     
    if response.status_code == 403:
        message_error = ('Ошибка авторизации: неверный или неактивен указанный ключ.')
        print(message_error)
        #error_message(message_error)
        for i in range(1, len(API_KEYS)):
            message_error = (f"Пробую другой ключ (осталось {len(API_KEYS) - i} попыток)")
            print(message_error)
            #error_message(message_error)
            
            HEADERS["X-Yandex-API-Key"] = API_KEYS[i]
            response = requests.get(URL, headers=HEADERS)
            
            if response.status_code == 200:
                break  # выходим из цикла, если удалось получить данные
        else:
            message_error = ('Яндекс.Кабинет разработчика.\n Сервис API Яндекс.Погоды заблокирован, так как превышено максимальное число запросов в сутки по вашему тарифу')
            print(message_error)
            error_message(message_error)
            return None
        
    if response.status_code == 200:
        
        data=response.json()
    
         # Сложный механизм обработки данных из ответа JSON (получение всех возможных параметров)     
        fact_data=data['fact']
        weather_condition=fact_data['condition']
        temperature=fact_data['temp']
        feels_like_temp=fact_data['feels_like'] 
        pressure_mmHg=(fact_data['pressure_mm'])
        humidity_percent=(fact_data['humidity'])
        wind_speed_msec=(fact_data["wind_speed"])
        
       # Обработка значения переменной weather
        
        if 'cloudy' in weather_condition:
            weather='облачно с прояснениями на фазенде 🌤️'
        elif 'rain' in weather_condition:
            weather='Дождь 🌧️'
        elif 'thunderstorm' in weather_condition:
            weather='Гроза'
        elif 'showers' in weather_condition:
            weather='Ливень 🌨️'
        elif 'overcast' in weather_condition:
            weather='Пасмурно ☁️'
        elif 'light-rain' in weather_condition:
            weather='Слегка моросит'
        elif 'heavy-rain' in weather_condition:
            weather='Ливень'
        elif 'thunderstorm-with-rain' in weather_condition:
            weather='Гроза'   
                   
    else: 
        message_error = ("Ошибка при запросе данных с сервера. Код ошибки: {response.status_code}")
        print(message_error)
        error_message(message_error)
        return None
      
    prev_weather = weather_condition  # сохраняем значение погоды для последующего использования
    return(f'Сейчас {weather}. '+
            f'\nТемпература: {temperature}°C.'+
            f'\nОщущается как: {feels_like_temp}°C.'+
            f'\nДавление: {pressure_mmHg} мм рт. ст.'+
            f'\nВлажность: {humidity_percent}%'+
            f'\nСкорость ветра: {wind_speed_msec} м/c.')
def wheather():
    # Добавляем объявление переменной
    global prev_weather 
    global weather_condition
    global current_weather
    
    # Бесконечный цикл проверки погоды
    while True:       

        # Получение текущей погоды через API Яндекс.Погода 
        current_weather = get_weather()

        weather_info = (f'\nТемпература: {temperature}°C.'+
                       f'\nОщущается как: {feels_like_temp}°C.'+
                        f'\nДавление: {pressure_mmHg} мм рт. ст.'+
                        f'\nВлажность: {humidity_percent}%'+
                        f'\nСкорость ветра: {wind_speed_msec} м/c.')

        # Если текущая погода отличается от предыдущей, отправляем сообщение
        dozhd = ['rain', 'thunderstorm', 'showers', 'light-rain', 'thunderstorm-with-rain', 'heavy-rain']
        if prev_weather not in dozhd and weather_condition in dozhd:
                send_message(f'🌧️ Дождь на фазенде.\n{weather_info}')
                print (f'🌧️ Дождь на фазенде.\n{weather_info}')
        elif prev_weather in dozhd and weather_condition == 'overcast' :
                send_message(f'Дождь окончен, ☁️ Облачно на фазенде.\n{weather_info}')
                print (f'Дождь окончен, ☁️ Облачно на фазенде.\n{weather_info}')
        elif prev_weather in dozhd and weather_condition == 'cloudy'  :
                send_message(f'Дождь окончен, 🌤️ Облачно с прояснениями на фазенде.\n{weather_info}')
                print (f'Дождь окончен, 🌤️ Облачно с прояснениями на фазенде.\n{weather_info}')
        elif prev_weather in dozhd and weather_condition == 'clear':
                send_message(f'Дождь окончен, ☀️ Солнечно на фазенде.\n{weather_info}')
                print(f'Дождь окончен, ☀️ Солнечно на фазенде.\n{weather_info}')
        elif prev_weather == None:
                send_message(f'Отслеживание дождя на фазенде запушено...\n{current_weather}')
                print (f'Запуск.\n{current_weather} ')
        else:
            print(f'Сервисное уведомление для тестирования:\nпогода работает, было: {prev_weather}, сейчас: {weather_condition}')
            time.sleep(2)
            #   пасмурно.
            if prev_weather == 'overcast':
                print(f'{current_weather}')
            elif prev_weather == 'clear':
                print(f'{current_weather}')
            #   облачно с прояснениями
            elif prev_weather == 'cloudy':
                print(f'{current_weather}')
        prev_weather = weather_condition
        time.sleep(300)
        
   # Задерживаем выполнение программы на нужное количество секунд
# Начинаем выполнение задания через ближайшие 5 минут от текущего времени
# Определяем текущее время
now = datetime.datetime.now()

# Вычисляем сколько осталось до следующей пятиминутки
delta_minutes = (5 - now.minute % 5)

# Запускаем задание через определенное количество секунд
time.sleep(delta_minutes * 60)

schedule.every().hour.at(":05").do(wheather)
schedule.every().hour.at(":10").do(wheather)
schedule.every().hour.at(":15").do(wheather)
schedule.every().hour.at(":20").do(wheather)
schedule.every().hour.at(":25").do(wheather)
schedule.every().hour.at(":30").do(wheather)
schedule.every().hour.at(":35").do(wheather)
schedule.every().hour.at(":40").do(wheather)
schedule.every().hour.at(":45").do(wheather)
schedule.every().hour.at(":50").do(wheather)
schedule.every().hour.at(":55").do(wheather)
schedule.every().hour.at(":00").do(wheather)

while True:
    schedule.run_pending()
    time.sleep(1)

