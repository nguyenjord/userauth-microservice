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
    """
    Desc: Create a new session for a logged in user.
    Input: string - username
    Output: Stores session in SESSIONS
    Return: string - session_id
    """

    # Create session id
    session_id = str(random.randint(LO_RAN_NUM, HI_RAND_NUM))

    # Store active user in current session list
    SESSIONS[session_id] = username

    return session_id

def validate_session(session_id):
    """
    Desc: Check if a session ID is valid.
    Input: string - session_id
    Output: None
    Return: string - username if valid, None if invalid
    """

    if session_id and session_id in SESSIONS:
        return SESSIONS[session_id]
    return None

def process_request(data):
    """
    Desc: Route incoming requests to the correct function based on action (with action map).
    Input: dict - data containing action and request parameters
    Output: None
    Return: dict - response from the appropriate function
    """

    action = data.get("action", "").strip()
    handler = ACTION_MAP.get(action, login_request)  # Get action from action map
    return handler(data) 

    
def success_response(message, **extra_fields):
    """
    Desc: Create a standard success response dictionary.
    Input: string - message, optional key-value pairs
    Output: None
    Return: dict - response with status "ok" and message
    """

    response = {
        "status": "ok",
        "message": message
    }
    response.update(extra_fields)
    return response

def error_response(message, **extra_fields):
    """
    Desc: Create a standard error response dictionary.
    Input: string - message, optional key-value pairs
    Output: None
    Return: dict - response with status "error" and message
    """

    response = {
        "status": "error",
        "message": message
    }
    response.update(extra_fields)
    return response

def login_request(data):
    """
    Desc: Check username and password, create session if valid.
    Input: dict - data containing username and password
    Output: Creates session in SESSIONS if successful
    Return: dict - success response with session_id or error response
    """

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

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
    """
    Desc: End user session and remove session data.
    Input: dict - data containing session_id
    Output: Removes session from SESSIONS if valid
    Return: dict - success or error response
    """

    session_id = data.get("session_id")

    # If no session_id
    if not session_id:
        return error_response("Missing session_id")

    username = validate_session(session_id)
    
    # If valid session
    if username:
        del SESSIONS[session_id]
        return success_response("Logout successful")
    else:
        return error_response("Invalid or expired session_id")
    
def reset_code_request(data):
    """
    Desc: Generate a reset code for password recovery.
    Input: dict - data containing username
    Output: Stores reset code in RESET_CODES
    Return: dict - success response with reset_code or error response
    """   

    username = str(data.get("username", "")).strip()

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

def reset_password(data):
    """
    Desc: Update user password with a valid reset code.
    Input: dict - data containing username, reset_code, and new_password
    Output: Updates password in USERS and users.json, removes reset code from RESET_CODES
    Return: dict - success or error response
    """

    username = str(data.get("username", "")).strip()
    reset_code = str(data.get("reset_code", "")).strip()
    new_password = str(data.get("new_password", "")).strip()

    # Check missing fields
    if not username or not reset_code or not new_password:
        return error_response("Missing username, reset_code, or new_password")

    # Check if username has reset code
    if username not in RESET_CODES:
        return error_response("No reset code found for this user")
    
    # Check if reset code matches
    if RESET_CODES[username] != reset_code:
        return error_response("Invalid reset code")
    
    # Update password in USERS
    USERS[username] = new_password

    # Save updated USERS to users.json
    with open("users.json", "w") as f:
        json.dump(USERS, f, indent=4)

    # Remove the reset code
    del RESET_CODES[username]

    return success_response("Password has been reset successfully", username=username)

def create_user(data):
    """
    Desc: Register a new user with username and password.
    Input: dict - data containing username and password
    Output: Adds user to USERS and saves to users.json
    Return: dict - success response with username or error response
    """

    username = str(data.get("username", "")).strip()
    password = str(data.get("password", "")).strip()

    # Check missing fields
    if not username or not password:
        return error_response("Missing username, or password for registration")

    # Username already exists
    if username in USERS:
        return error_response("Username already exists")

    # Add user to USERS json and save
    USERS[username] = password
    with open("users.json", "w") as f:
        json.dump(USERS, f, indent=4)   

    return success_response("User registered successfully", username=username)

ACTION_MAP = {
    "logout": logout_request,
    "reset_request": reset_code_request, # Reset code if user request new password
    "reset_password": reset_password,  # If reset code matches, reset password
    "register": create_user, # Create new user, add password to json file
    "login": login_request # call login function if not logout
}

def main():
    """
    Desc: Start the ZeroMQ server and listen for authentication requests.
    Input: None
    Output: Prints server status, processes incoming requests
    Return: None
    """

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
            socket.send_string(json.dumps(error_response("Invalid JSON")))
            continue

        # Get user action
        reply_data = process_request(data)

        # Convert to JSON string
        reply_json = json.dumps(reply_data)

        # Send reply back to the client
        socket.send_string(reply_json)

if __name__ == "__main__":
    main()
        