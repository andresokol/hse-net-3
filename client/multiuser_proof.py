import asyncio


async def tcp_echo_client(message, loop):
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888,
                                                   loop=loop)

    print('Send: %r' % message)
    writer.write(message.encode())

    data = await reader.read(100)
    print('Received: %r' % data.decode())

    print('Close the socket')
    writer.close()


async def main(loop):
    import random
    message = 'Hello World!' + str(random.randint(0, 10))
    await asyncio.gather(tcp_echo_client(message, loop), tcp_echo_client(message, loop),
                         tcp_echo_client(message, loop), tcp_echo_client(message, loop), loop=loop)


loop = asyncio.get_event_loop()
loop.run_until_complete(main(loop))
loop.close()
