Репозиторий с кодм 2 облачных функций которые совместно реализуют бота Кто это.


В папке queue_reader лежит функция, которую нужно установить как триггер для MessageQueue

в папке webhook лежит обработчик вебхуков от телеграма. 
чтобы привязать бота нужно выполнить в терминале

```shell
 curl -F "url=https://functions.yandexcloud.net/{cloud-function-id}" https://api.telegram.org/bot{bot-token}/setWebhook
```

Для обеих функций нужны следуюющие настройки
Переменные среды

aws_id, aws_id - ключи сервиного аккаунта

bot_token - токен бота

bucket - бакет Object Storage, откуда будем брать файлы

queue_url - url очереди, откуда будем брать сообщения
