import zmq
import json

# Load users from users.json into a Python dictionary
with open("users.json") as f:
    USERS = json.load(f)

def login_data(data):

    username = data.get("username")
    password = data.get("password")

    # Check missing fields
    if not username or not password:
        return {
            "status": "error",
            "username": username or "",
            "authenticated": False,
            "message": "Missing username or password"
        }
    
    # Check if the username exists and the password matches users.json
    if username in USERS and USERS[username] == password:
        return {
            "status": "ok",
            "username": username,
            "authenticated": True,
            "message": "Login successful"
        }
    
    # Return Invalid prompt
    else:
        return {
            "status": "error",
            "username": username,
            "authenticated": False,
            "message": "Invalid username or password"
        }    
    
def main():

    # Step up ZeroMQ
    context = zmq.Context()

    # REP socket
    socket = context.socket(zmq.REP)

    # Bind(addr): This is the address string. This is where the socket will listen
    # on the network port. FORMAT: protocol://interface:port
    socket.bind("tcp://*:5555")
    print("User Authentication Microservice listening on tcp://*:5555")

    while True:

        # Message from the client, recieves message from the client
        # This will be blank since we will wait until the message arrives
        message = socket.recv_string()
        
        print("Server Received: ", message)

        try:
            data = json.loads(message)
        except json.JSONDecodeError:

            # Check if valid JSON
            socket.send_string("Invalid JSON")
            continue

        # Pull username and password
        reply_data = login_data(data)

        # Convert to JSON string

        reply_json = json.dumps(reply_data)

        # Send reply back to the client
        socket.send_string(reply_json)

if __name__ == "__main__":
    main()
        