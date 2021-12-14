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


### Пример работы клиента

```bash
$ python3 client/client.py --host localhost --port 8080
Establishing connection with localhost:8080... done!
Username: andresokol
Password: andresokol
Unknown user, want to register? y/n: y
Registered successfully
- - - - - - - - - - - - - - - - - - - - 
Welcome, andresokol!
- - - - - - - - - - - - - - - - - - - - 

0: Set new task
> 0
Timestamp of shoot: 20 
Enter timestamp in ISO format - e.g. 2020-03-02 10:00
Timestamp of shoot: 2021-12-14 13:42
Shot longitude: 74
Shot latitude: 95
Should be correct angle from -90 to 90
Shot latitude: 77
- - - - - - - - - 
Please, confirm new task
Timestamp: 2021-12-14 13:42:00
Longitude: 74.0
Latitude: 77.0
Submit? [y/n]
y
Task successfully created with id 494E7B

0: Set new task
1: Select task 494E7B
> 1
- - - Task 494E7B - - -
Coordinates: 74, 77
Time to shoot: 2021-12-14 13:42:00
Should be ready in 0:01:43.862051
- - - - - - - - - - - - 
f: Try to fetch the result
b: Back to task list
> f
Result of the shoot is not yet ready
f: Try to fetch the result
b: Back to task list
```

```bash
$ python3 client/client.py --host localhost --port 8080
Establishing connection with localhost:8080... done!
Username: andresokol
Password: andresokol
Login successful!
- - - - - - - - - - - - - - - - - - - - 
Welcome, andresokol!
- - - - - - - - - - - - - - - - - - - - 

0: Set new task
1: Select task 494E7B
> 1
- - - Task 494E7B - - -
Coordinates: 74, 77
Time to shoot: 2021-12-14 13:42:00
Should be available
- - - - - - - - - - - - 
f: Try to fetch the result
b: Back to task list
> f
============================= Result of shoot 494E7B =============================
|     o                                                       .              ,   |
|                                                                           .    |
|                                          o                                     |
|                                         ,                                      |
|   `                                                        o                   |
|                                                                                |
|                                                                                |
|                                                          *                     |
|                                           .                                    |
|                                                                                |
============================= Result of shoot 494E7B =============================
f: Try to fetch the result
b: Back to task list
> 
```

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