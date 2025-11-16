import zmq

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

        # Send reply back to the client
        socket.send_string("OK")
        