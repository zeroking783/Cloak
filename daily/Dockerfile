# Используем базовый Python образ
FROM python:3.10

# Обновляем пакеты и устанавливаем cron
RUN apt-get update -y && apt-get install -y cron

# Устанавливаем рабочую директорию
WORKDIR /app/Cloak_daily

# Копируем requirements.txt и устанавливаем зависимости
COPY ../requirements.txt ./
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

COPY . ./

# Копируем cron файл и даем ему нужные права
RUN mv crontab /etc/cron.d/cron_Cloak
RUN chmod 0644 /etc/cron.d/cron_Cloak

# Добавляем cron файл в crontab
RUN crontab /etc/cron.d/cron_Cloak

# Создаем файл лога для cron
RUN touch /var/log/cron.log

# Запускаем cron в фоновом режиме и отслеживаем логи
CMD cron && tail -f /var/log/cron.log
