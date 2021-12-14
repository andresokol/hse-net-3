import argparse
import asyncio
import datetime as dt
import socket
import sys

INPUT_PREFIX = '> '


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

    async def draw_result(self, task_id):
        code, response = await self.communicate(f'GETRESULT {task_id}')
        if code == '202':
            print('Result of the shoot is not yet ready')
            return
        elif code != '200':
            print('Unresolved server error')
            return

        data = response.split()[1].replace('_', ' ')

        print('=' * 29, f'Result of shoot {task_id}', '=' * 29)
        for i in range(10):
            print('|', data[80 * i: 80 * (i + 1)], '|', sep='')
        print('=' * 29, f'Result of shoot {task_id}', '=' * 29)

    async def create_task(self):
        date = None
        x_angle = None
        y_angle = None
        while date is None:
            try:
                date = dt.datetime.fromisoformat(input('Timestamp of shoot: '))
            except ValueError:
                print('Enter timestamp in ISO format - e.g. 2020-03-02 10:00')

        while True:
            try:
                x_angle = float(input('Shot longitude: '))
                assert -90.0 <= x_angle <= 90.0
                break
            except (ValueError, AssertionError):
                print('Should be correct angle from -90 to 90')

        while True:
            try:
                y_angle = float(input('Shot latitude: '))
                assert -90.0 <= y_angle <= 90.0
                break
            except (ValueError, AssertionError):
                print('Should be correct angle from -90 to 90')

        print('- - - - - - - - - ')
        print(f'Please, confirm new task')
        print(f'Timestamp: {date}')
        print(f'Longitude: {x_angle}')
        print(f'Latitude: {y_angle}')

        will = None
        while will not in ['y', 'n']:
            will = input('Submit? [y/n]\n')

        if will == 'n':
            return

        code, resp = await self.communicate(f'SETTASK {x_angle} {y_angle} {date.isoformat()}')
        if code == '201':
            task_id = resp.split()[1]
            print('Task successfully created with id', task_id)
        elif code == '405':
            print('ERROR - Timeslot is not empty or in the past, try another slot')
        else:
            print('ERROR - Unknown server error')

    async def register_loop(self, username, password):
        will = None
        while will not in ['y', 'n']:
            will = input('Unknown user, want to register? y/n: ').lower()

        if will.lower() == 'n':
            return

        code, response = await self.communicate(f'REGISTER {username} {password}')

        if code != '201':
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
        print(f'- - - Task {task_id} - - -')
        print(f'Coordinates: {x_angle}, {y_angle}')
        print(f'Time to shoot: {date}')
        if date > dt.datetime.now():
            print(f'Should be ready in {date - dt.datetime.now()}')
        else:
            print(f'Should be available')
        print('- ' * 12)
        while True:
            print('f: Try to fetch the result')
            print('b: Back to task list')
            option = input(INPUT_PREFIX)
            if option == 'b':
                return
            elif option == 'f':
                await self.draw_result(task_id)
            else:
                print('Unrecognized, enter "f" or "b"')

    async def logic_loop(self):
        await self.auth_loop()

        print('- ' * 20)
        print(f'Welcome, {self.username}!')
        print('- ' * 20)

        while True:
            code, response = await self.communicate('TASKLIST')

            tasks = response.split()[1:]
            print()
            print('0: Set new task')
            for i in range(len(tasks)):
                print(f'{i + 1}: Select task {tasks[i]}')

            choice = input(INPUT_PREFIX)
            if not choice.isnumeric() or int(choice) > len(tasks) + 1:
                continue

            if choice == '0':
                await self.create_task()
            else:
                task_id = tasks[int(choice) - 1]
                await self.task_loop(task_id)


async def main(host, port):
    print(F'Establishing connection with {host}:{port}...', end='')
    sys.stdout.flush()

    future = asyncio.wait_for(asyncio.open_connection(host, port), 10)
    try:
        reader, writer = await future
    except ConnectionRefusedError as exc:
        print(f' Error! Host "{host}" refusing connection on port {port}')
        return
    except socket.gaierror as exc:
        print(f' Error! Cannot resolve host "{host}"')
        return
    except asyncio.exceptions.TimeoutError:
        print(f' Error! Connection to "{host}:{port}" timed out')
        return

    print(' done!')

    app = ClientApp(reader, writer)
    await app.logic_loop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, help='IP to bind to')
    parser.add_argument('--port', required=True, help='port to bind to')
    args = parser.parse_args()

    asyncio.run(main(args.host, args.port))
