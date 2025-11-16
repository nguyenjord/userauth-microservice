import zmq
import json
import random

# Random Digit Constants
LO_RAN_NUM = 100000
HI_RAND_NUM = 999999

# Load users from users.json into a Python dictionary
with open("users.json") as f:
    USERS = json.load(f)

# Store active session
SESSIONS = {}

# Password reset codes
RESET_CODES = {}

def create_session(username):

    # Create session id
    session_id = str(random.randint(LO_RAN_NUM, HI_RAND_NUM))

    # Store active user in current session list
    SESSIONS[session_id] = username

    return session_id

def process_request(data):

    user_action = data.get("action")

    if user_action == "logout":
        return logout_request(data)
    
    # call login function if not logout
    return login_request(data)

def success_response(message, **extra_fields):
    
    response = {
        "status": "ok",
        "message": message
    }
    response.update(extra_fields)
    return response

def error_response(message, **extra_fields):
    
    response = {
        "status": "error",
        "message": message
    }
    response.update(extra_fields)
    return response

def login_request(data):

    username = str(data.get("username"))
    password = str(data.get("password"))

    # Check if missing fields
    if not username or not password:
        return error_response(
            "Missing username or password",
            username=username or "",
            authenticated=False
            )
        
    # Check if username exists and the password matches users.json
    if username in USERS and USERS[username] == password:

        session_id = create_session(username)

        return success_response(
            "Login successful",
            username=username,
            authenticated=True,
            session_id=session_id
        )
    
    # Return Invalid prompt
    else:
        return error_response(
            "Invalid username or password",
            username=username,
            authenticated=False
        )

def logout_request(data):

    session_id = data.get("session_id")

    # If no session_id
    if not session_id:
        return error_response("Missing session_id")

    # Check if the session exists
    if session_id in SESSIONS:
        # Remove the active session
        del SESSIONS[session_id]
        return success_response("Logout successful")
    
    else:
        return error_response("Invalid or expired session_id")
    
def reset_request(data):
    
    username = str(data.get("username", ""))

    # Check if username is missing
    if not username:
        return error_response("Username missing")
    
    # Check if user exists
    if username not in USERS:
        return error_response("Username not found")
    
    # Create reset code
    reset_code = str(random.randint(LO_RAN_NUM, HI_RAND_NUM))

    # Store temp code w/USER
    RESET_CODES[username] = reset_code

    # Return reset_code
    return success_response(
        "Reset code generated",
        username=username,
        reset_code=reset_code
    )


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
        