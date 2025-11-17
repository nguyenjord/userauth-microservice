User Authentication Microservice (CS361)

This microservice provides Login, Logout, and Password Reset functionality.

Communication happens through ZeroMQ with JSON formatted messages.

## How to Run the Microservice

1. Navigate to the microservice folder: 

- cd user-auth

2. Run the service:

- python3 app.py

3. Service will start listening on:

- tcp://localhost:5555
- Keep system running

## How to Communicate With the Microservice

All communication happens using ZeroMQ REQ/REP sockets.

Clients must:
- Connect to: tcp://localhost:5555
- Send a JSON string
- Receive a JSON string in response

## Actions
Below are the valid JSON messages a user can send to this microservice.

### 1.Login

Request:
{
  "username": "test",
  "password": "password123"
}

Success Response:
{
  "status": "ok",
  "message": "Login successful",
  "username": "test",
  "authenticated": true,
  "session_id": "123456"
}

Fail Response:
{
  "status": "error",
  "message": "Invalid username or password",
  "authenticated": false
}

### 2.Logout

Request:
{
  "action": "logout",
  "session_id": "123456"
}

Success Response:
{
  "status": "ok",
  "message": "Logout successful"
}

Fail Response:
{
  "status": "error",
  "message": "Invalid or expired session_id"
}


### 3.Request Password Reset

Generates a temporary reset code for a valid username.

Request:
{
  "action": "reset_request",
  "username": "test"
}

Success Response:
{
  "status": "ok",
  "message": "Reset code generated",
  "username": "test",
  "reset_code": "123456"
}

### 4. Reset Password

Uses a valid reset code to update the user’s password.

Request:
{
  "action": "reset_password",
  "username": "test",
  "reset_code": "123456",
  "new_password": "newpass123"
}

Success Response:
{
  "status": "ok",
  "message": "Password has been reset successfully",
  "username": "test"
}

## Data Storage

user.json

This file stores persistent username/password:
{
  "test1": "abc123",
  "test2": "abc123",
  "test3": "password123"
}

Microservice Run Time Storage
- SESSIONS: active session IDs
- RESET_CODES: temporary password reset codes

These are created and deleted when service starts/ends

## Notes
- You do not need your own users.json file.
- Use existing usernames, or ask the microservice owner to add one.
- Always send requests as valid JSON strings over ZeroMQ.
- The service replies only after receiving a message (REQ/REP behavior).
- Do not store any passwords in your own microservice let this service handle all auth.

## Python Client Example

import zmq
import json

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

request = {
    "username": "jose",
    "password": "password123"
}

socket.send_string(json.dumps(request))
reply = socket.recv_string()
print("Reply:", reply)


## License
This project is for academic use.