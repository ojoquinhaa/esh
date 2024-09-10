import asyncio
import websockets
import subprocess
import os
import platform
import pyfiglet
import dotenv

dotenv.load_dotenv()

def get_whoami():
    result = subprocess.run(['whoami'], capture_output=True, text=True)
    return result.stdout.strip()

async def send_prefix(websocket, current_dir):
    os_type = platform.system()
    if os_type == "Windows":
        await websocket.send(f"PS {current_dir}> ")
    else:
        user = get_whoami()
        hostname = platform.node()

        await websocket.send(f"{user}@{hostname}$ ")

async def handle_terminal(websocket):
    banner = pyfiglet.figlet_format("E-SHELL")

    welcome_message = (
        f"{banner}\n"
        "Welcome to E-SHELL!\n"
        "A simple WebSocket-based terminal emulator.\n"
        "Author: ojoquinhaa\n"
        "Type your commands below, or use 'cd' to change directories.\n"
        "Type 'exit' to close the session.\n"
    )

    current_dir = os.getcwd()
    await websocket.send(welcome_message)

    await send_prefix(websocket, current_dir)

    async for command in websocket:
        command = command.strip()
        
        if command.lower() == "exit":
            await websocket.send("Session closed.")
            break
        elif command.startswith("cd "):
            try:
                new_dir = command[3:].strip()
                os.chdir(new_dir)
                current_dir = os.getcwd()
                await websocket.send(f"Directory changed to: {current_dir}\n")
            except FileNotFoundError:
                await websocket.send(f"Error: Directory '{new_dir}' not found.\n")
            except Exception as e:
                await websocket.send(f"Error: {str(e)}\n")
        else:
            try:
                output = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=current_dir)
                response = output.stdout + output.stderr
                await websocket.send(response)
            except Exception as e:
                await websocket.send(f"Error: {str(e)}")

        await send_prefix(websocket, current_dir)

async def main():
    HOST = os.getenv('HOST') or 'localhost'
    PORT = int(os.getenv('PORT')) or 8001

    try:
        async with websockets.serve(handle_terminal, HOST, PORT):
            print(f"ESH Websocket running in port {PORT}")
            await asyncio.Future()
    except KeyboardInterrupt:
        print('Exiting...')

if __name__ == "__main__":
    asyncio.run(main())
