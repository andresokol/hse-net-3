import asyncio
import datetime as dt
import sqlite3
import typing as tp
import random
import uuid

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8888


def gen_result():
    x = 10
    y = 80
    res = ''
    print('_' * y)
    for i in range(x):
        for j in range(y):
            if random.random() > 0.015:
                res += '_'
                print(' ', end='')
            else:
                c = random.choice('.*\'`,o')
                res += c
                print(c, end='')
        print()
    print('_' * y)
    return res


class ServerAppException(Exception):
    response = '500'

    def __init__(self):
        super().__init__()


class ServerAppBadRequest(ServerAppException):
    response = '400'


class ServerAppNoLogin(ServerAppException):
    response = '401'


class ServerAppNotRegistered(ServerAppException):
    response = '402'


class ServerAppBadCredentials(ServerAppException):
    response = '403'


class ServerAppNotFound(ServerAppException):
    response = '404'


class ServerAppNotAllowed(ServerAppException):
    response = '405'


class ServerAppUnsupportedCommand(ServerAppException):
    response = '501'


class ServerContext:
    user: tp.Optional[str] = None
    is_authorized: bool = False


DDL = '''
CREATE TABLE IF NOT EXISTS tasks (
    id           TEXT          PRIMARY KEY,
    author       TEXT          NOT NULL,
    x_angle      DECIMAL(7, 4) NOT NULL,
    y_angle      DECIMAL(7, 4) NOT NULL,
    start_time   TIMESTAMP NOT NULL,
    photo_result TEXT
);
'''

DDL2 = '''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
);
'''


class ServerApp:
    def __init__(self):
        self.connection = sqlite3.connect('server.sqlite')

        # checking tables
        c = self.connection.cursor()
        c.execute(DDL)
        c.execute(DDL2)
        self.connection.commit()
        print('Created connection to DB')

    def __del__(self):
        print('Closing connection to DB')
        self.connection.commit()
        self.connection.close()

    def _handle_register(self, args: tp.List[str],
                         context: ServerContext) -> tp.Tuple[str, ServerContext]:
        if len(args) != 2:
            raise ServerAppBadRequest()

        try:
            cursor = self.connection.cursor()
            cursor.execute('INSERT INTO users VALUES (?, ?);', args)
            self.connection.commit()
        except sqlite3.Error:
            raise ServerAppNotAllowed()

        context.user = args[0]
        context.is_authorized = True
        return f'201', context

    def _handle_connect(self, args: tp.List[str],
                        context: ServerContext) -> tp.Tuple[str, ServerContext]:
        if len(args) != 2:
            raise ServerAppBadRequest()

        print(args)

        cursor = self.connection.cursor()
        cursor.execute('SELECT password FROM users WHERE username = ?;', [args[0]])
        res = cursor.fetchone()

        if not res:
            raise ServerAppNotRegistered()

        if res[0] != args[1]:
            raise ServerAppBadCredentials()

        context.user = args[0]
        context.is_authorized = True

        return '200', context

    def _handle_settask(self, args: tp.List[str],
                        context: ServerContext) -> tp.Tuple[str, ServerContext]:
        if not context.is_authorized:
            raise ServerAppNoLogin()

        if len(args) != 3:
            raise ServerAppBadRequest()

        try:
            x_angle, y_angle, start_time = args[0], args[1], args[2]
            x_angle = float(x_angle)
            y_angle = float(y_angle)
            start_time = dt.datetime.fromisoformat(start_time)

            assert -90.0 <= x_angle <= 90.0
            assert -90.0 <= y_angle <= 90.0
        except (ValueError, AssertionError):
            raise ServerAppBadRequest()

        task_id = uuid.uuid4().hex[::6].upper()

        if start_time < dt.datetime.now():
            raise ServerAppNotAllowed()

        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO tasks VALUES (?,?,?,?,?,?);',
                       [task_id, context.user, x_angle, y_angle, start_time, gen_result()])
        self.connection.commit()

        return f'201 {task_id}', context

    def _handle_tasklist(self, args: tp.List[str],
                         context: ServerContext) -> tp.Tuple[str, ServerContext]:
        if not context.is_authorized:
            raise ServerAppNoLogin()

        c = self.connection.cursor()
        c.execute('SELECT id FROM tasks WHERE author = ? ORDER BY start_time;', [context.user])

        result = c.fetchall()
        print(result)

        return '200 ' + ' '.join(map(lambda x: x[0], result)), context

    def _handle_gettask(self, args: tp.List[str],
                        context: ServerContext) -> tp.Tuple[str, ServerContext]:
        if not context.is_authorized:
            raise ServerAppNoLogin()

        task_id = args[0]
        c = self.connection.cursor()
        c.execute('SELECT x_angle, y_angle, start_time FROM tasks WHERE id = ? AND author = ?;',
                  [task_id, context.user])

        result = c.fetchone()
        print(result)
        if not result:
            raise ServerAppNotFound()

        return f'200 {result[0]} {result[1]} {result[2].replace(" ", "T")}', context

    def _handle_getresult(self, args: tp.List[str],
                          context: ServerContext) -> tp.Tuple[str, ServerContext]:
        if not context.is_authorized:
            raise ServerAppNoLogin()

        task_id = args[0]
        c = self.connection.cursor()
        c.execute('SELECT start_time, photo_result FROM tasks WHERE id = ? AND author = ?;',
                  [task_id, context.user])

        result = c.fetchone()
        print(result)
        if not result:
            raise ServerAppNotFound()

        result_dt = dt.datetime.fromisoformat(result[0])
        print(result_dt, dt.datetime.now())
        print(result_dt - dt.datetime.now())
        if result_dt > dt.datetime.now():
            return '202', context

        return f'200 {result[1]}', context

    _HANDLERS = {
        'REGISTER': _handle_register,
        'CONNECT': _handle_connect,
        'SETTASK': _handle_settask,
        'TASKLIST': _handle_tasklist,
        'GETTASK': _handle_gettask,
        'GETRESULT': _handle_getresult,
    }

    async def handle_connection(self, reader, writer):
        context = ServerContext()

        while True:
            data = await reader.read(1024)
            if not data:
                break

            try:
                message = data.decode().strip()
                addr = writer.get_extra_info('peername')
                print(f"[{addr!r}] {message!r}")
                args = message.split()

                handler = self._HANDLERS.get(args[0])
                if not handler:
                    raise ServerAppUnsupportedCommand()
                response_message, context = handler(self, args[1:], context)
                await asyncio.sleep(0.1)
            except ServerAppException as exc:
                response_message = exc.response
            except Exception as exc:
                print(f'ERR: {exc} {exc!r}')
                response_message = ServerAppException.response

            print(f"[{context.user if context.is_authorized else addr!r}]",
                  f"respond: {response_message!r}")
            writer.write(response_message.encode() + b'\r\n')
            await writer.drain()

        print("Close the connection")
        writer.close()


async def main():
    app = ServerApp()
    server = await asyncio.start_server(app.handle_connection, SERVER_HOST, SERVER_PORT)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
