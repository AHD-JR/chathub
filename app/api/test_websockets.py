import asyncio
import websockets

async def send_and_receive_message():
    sender_id = "AAAAAAAAAAAAAAAAAAAAAAAAA"
    uri = f"ws://localhost:8000/ws/{sender_id}"

    async with websockets.connect(uri) as websocket:
        print("WebSocket connection opened.")

        try:
            while True:
                message = input("Enter a message to send: ")
                await websocket.send(message)
                

                response = await websocket.recv()
                print("Received response:", response)
        except websockets.exceptions.ConnectionClosedOK as e:
            print(f"Closed cleanly, code={e.code}, reason={e.reason}")  
        except websockets.exceptions.ConnectionClosedError as e:
            print("Connection died with error:", e)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(send_and_receive_message())