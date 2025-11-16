import zmq
import json
import random

# Load users from users.json into a Python dictionary
with open("users.json") as f:
    USERS = json.load(f)

# Store active session
SESSIONS = {}

def login_request(data):

    username = str(data.get("username"))
    password = str(data.get("password"))

    # Check if missing fields
    if not username or not password:
        return {
            "status": "error",
            "username": username or "",
            "authenticated": False,
            "message": "Missing username or password"
        }
    
    # Check if username exists and the password matches users.json
    if username in USERS and USERS[username] == password:

        session_id = create_session(username)

        return {
            "status": "ok",
            "username": username,
            "authenticated": True,
            "session_id": session_id,
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

def create_session(username):

    # Create session id
    session_id = str(random.randint(100000, 999999))

    # Store active user in current session list
    SESSIONS[session_id] = username

    return session_id

def logout_request(data):

    session_id = data.get("session_id")

    # If no session_id
    if not session_id:
        return {
            "status": "error",
            "message": "Missing session_id"
        }

    # Check if the session exists
    if session_id in SESSIONS:
        # Remove the active session
        del SESSIONS[session_id]

        return {
            "status": "ok",
            "message": "Logout successful"
        }
    else:
        return {
            "status": "error",
            "message": "Invalid or expired session_id"
        }
    
def process_request(data):

    user_action = data.get("action")

    if user_action == "logout":
        return logout_request(data)
    
    # call login function if not logout
    return login_request(data)


def main():

    # Setup ZeroMQ
    context = zmq.Context()

    # REP socket
    socket = context.socket(zmq.REP)

    # Bind(addr): This is the address string. This is where the socket will listen
    # on the network port. FORMAT: protocol://interface:port
    socket.bind("tcp://*:5555")
    print("User Authentication Microservice listening on tcp://*:5555")

    while True:

        # Message from the client, recieves message from the client
        message = socket.recv_string()
        
        print("Server Received: ", message)

        try:
            data = json.loads(message)
        except json.JSONDecodeError:

            # Check if valid JSON
            socket.send_string("Invalid JSON")
            continue

        # Get user action
        reply_data = process_request(data)

        # Convert to JSON string
        reply_json = json.dumps(reply_data)

        # Send reply back to the client
        socket.send_string(reply_json)

if __name__ == "__main__":
    main()
        