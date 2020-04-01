import asyncio
import datetime as dt
import sys

SERVER_HOST = 'localhost'
SERVER_PORT = 8888


class ClientApp:
    is_logged_in: bool = False
    username: str

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    async def communicate(self, message):
        self.writer.write(f'{message}\r\n'.encode())
        response = (await self.reader.read(1024)).decode()
        code = response.split()[0]
        return code, response

    async def register_loop(self, username, password):
        will = None
        while will not in ['y', 'n']:
            will = input('Unknown user, want to register? y/n: ').lower()

        if will.lower() == 'n':
            return

        code, response = await self.communicate(f'REGISTER {username} {password}')

        if code != '200':
            raise Exception(response)

        print('Registered successfully')
        self.is_logged_in = True
        self.username = username
        return

    async def auth_loop(self):
        while not self.is_logged_in:
            username = input('Username: ')
            password = input('Password: ')

            code, response = await self.communicate(f'CONNECT {username} {password}')

            if code == '200':
                print('Login successful!')
                self.is_logged_in = True
                self.username = username
                return
            if code == '403':
                print('Password mismatch, try again')
                continue
            if code != '402':
                print(f'Unexpected server response code: {response}')
                raise Exception(response)

            await self.register_loop(username, password)

    async def task_loop(self, task_id):
        code, response = await self.communicate(f'GETTASK {task_id}')
        assert code == '200'

        params = response.split()
        x_angle, y_angle = params[1], params[2]
        date = dt.datetime.fromisoformat(params[3])
        while True:
            print(f'=== Task {task_id} ===')
            print(f'Coordinates: {x_angle}, {y_angle}')
            print(f'Time to shoot: {date}')
            if date > dt.datetime.now():
                print(f'Should be ready in {date - dt.datetime.now()}')
            else:
                print(f'Should be available')
            return

    async def logic_loop(self):
        await self.auth_loop()
        assert self.is_logged_in  # FIXME

        print('- ' * 20)
        print(f'Welcome, {self.username}!')
        print('- ' * 20)

        while True:
            code, response = await self.communicate('TASKLIST')

            tasks = response.split()[1:]
            print('0: Set new task')
            for i in range(len(tasks)):
                print(f'{i + 1}: Select task {tasks[i]}')
            print()

            choice = input('> ')
            if not choice.isnumeric() or int(choice) > len(tasks) + 1:
                continue

            if choice == '0':
                continue
            else:
                task_id = tasks[int(choice) - 1]
                await self.task_loop(task_id)


async def main():
    print(F'Establishing connection with {SERVER_HOST}:{SERVER_PORT}...', end='')
    sys.stdout.flush()
    try:
        reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
    except OSError:
        print(' connection failed :(')
        return

    print(' done!')

    app = ClientApp(reader, writer)
    await app.logic_loop()
    # username = input('Username: ')
    # password = input('Password: ')
    #
    # if code == '402':
    #     print('No such user found, want to register?')
    # elif code == '403':
    #     print('Bad password, try again')
    # else:
    #     print()

    #
    # message = 'dsfsdfsdf'
    # print(f'Send: {message!r}')
    # writer.write(message.encode())
    #
    # data = await reader.read(100)
    # print(f'Received: {data.decode()!r}')
    #
    # print('Close the connection')
    # writer.close()


if __name__ == '__main__':
    # try:
    asyncio.run(main())
    # except:
    #     pass
