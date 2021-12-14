### Андрей Соколов, БПМИ-166, протокол автоматической обсерватории

Программы запускаются с Python 3.7+

Для запуска программы сервера:
```bash
python3 server/server.py --host localhost --port 8080
```

Для запуска программы клиента:
```bash
python3 client/client.py --host localhost --port 8080
```

Для сохранения данных на сервере между запусками используется SQLite, создается файл `server.sqlite`. Для сброса данных следует удалить этот файл.

Библиотека для работы с SQLite поставляется вместе с интерпретатором Python, так что никаких дополнительных библиотек потребоваться не должно.


### Примеры сетевых ошибок

```bash
$ python3 client/client.py --host localhost --port 8080
Establishing connection with localhost:8080... Error! Host "localhost" refusing connection on port 8080

$ python3 client/client.py --host localhosted --port 8080
Establishing connection with localhosted:8080... Error! Cannot resolve host "localhosted"

$ python3 client/client.py --host ddd.yandex.ru --port 8080
Establishing connection with ddd.yandex.ru:8080... Error! Connection to "ddd.yandex.ru:8080" timed out

$ python3 client/client.py --host ddd.andresokol.work --port 8080
Establishing connection with ddd.andresokol.work:8080... Error! Cannot resolve host "ddd.andresokol.work"
```