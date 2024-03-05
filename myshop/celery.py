import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings') # задается переменная DJANGO_SETTINGS_MODULE для встроенной в  Celery программы командной строки;

app = Celery('myshop') # создается экземпляр приложения;
app.config_from_object('django.conf:settings', namespace='CELERY') # спользуя метод config_from_object(), загружается любая конкретно прикладная конфигурация из настроек проекта. Атрибут namespace задает префикс, который будет в  вашем файле settings.py у  настроек, связанных с Celery. Задав именное пространство CELERY, все настройки Celery должны включать в  свое имя префикс CELERY_ (например, CELERY_BROKER_URL);
app.autodiscover_tasks() # аконец, сообщается, чтобы очередь заданий Celery автоматически обнаруживала асинхронные задания в  ваших приложениях. Celery будет искать файл tasks.py в каждом каталоге приложений, добавленных в INSTALLED_APPS, чтобы загружать определенные в нем асинхронные задания.