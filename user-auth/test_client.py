import zmq
import json

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    print("Client connected to User Authentication Microservice")

    username = "jose"
    old_password = "password123"      # must match users.json initially
    new_password = "123"   # whatever new password you want

    # 1) LOGIN WITH OLD PASSWORD (optional sanity check)
    print("\n--- Step 1: Login with OLD password ---")
    login_request = {
        "username": username,
        "password": old_password
    }
    socket.send_string(json.dumps(login_request))
    login_reply_json = socket.recv_string()
    print("Login (old pw) reply:", login_reply_json)

    # 2) REQUEST RESET CODE
    print("\n--- Step 2: Request reset code ---")
    reset_request = {
        "action": "reset_request",
        "username": username
    }
    socket.send_string(json.dumps(reset_request))
    reset_reply_json = socket.recv_string()
    print("Reset request reply:", reset_reply_json)

    reset_reply = json.loads(reset_reply_json)
    reset_code = reset_reply.get("reset_code")
    print("Reset code received:", reset_code)

    if not reset_code:
        print("No reset_code returned; cannot continue reset flow.")
        return

    # 3) CONFIRM RESET WITH CODE + NEW PASSWORD
    print("\n--- Step 3: Reset password with code + new password ---")
    reset_password_request = {
        "action": "reset_password",   # <— matches your process_request
        "username": username,
        "reset_code": reset_code,
        "new_password": new_password
    }
    socket.send_string(json.dumps(reset_password_request))
    reset_password_reply_json = socket.recv_string()
    print("Reset password reply:", reset_password_reply_json)

    # 4) TRY LOGIN AGAIN WITH NEW PASSWORD
    print("\n--- Step 4: Login with NEW password ---")
    new_login_request = {
        "username": username,
        "password": new_password
    }
    socket.send_string(json.dumps(new_login_request))
    new_login_reply_json = socket.recv_string()
    print("Login (new pw) reply:", new_login_reply_json)

if __name__ == "__main__":
    main()


