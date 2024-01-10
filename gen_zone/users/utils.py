# Импорт класса для отправки электронных писем в Django
from django.core.mail import EmailMessage

# Импорт модуля для работы с многопоточностью
import threading

# Класс EmailThread наследуется от threading.Thread и предназначен для отправки электронных писем в отдельном потоке
class EmailThread(threading.Thread):

    # Конструктор класса, принимающий объект email, который представляет собой письмо
    def __init__(self, email):
        # Присвоение переданного письма объекту email внутри класса
        self.email = email
        # Вызов конструктора базового класса threading.Thread
        threading.Thread.__init__(self)

    # Метод run выполняется при запуске потока
    def run(self):
        # Отправка письма, вызывая метод send у объекта email
        self.email.send()

# Класс Util содержит статический метод для отправки электронных писем
class Util:
    @staticmethod
    def send_email(data):
        # Создание объекта EmailMessage с переданными данными
        email = EmailMessage(
            subject=data['email_subject'],  # Тема письма
            body=data['email_body'],  # Текст письма
            to=[data['to_email']]  # Получатели письма
        )
        
        # Создание и запуск отдельного потока (EmailThread) для отправки письма
        EmailThread(email).start()