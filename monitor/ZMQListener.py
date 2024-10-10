import zmq

class ZMQListener:
    def __init__(self, callbacks):
        # Initialize ZeroMQ context and sockets
        self.context = zmq.Context()
        
        self.sockets = {
            "zmqpubhashtx": self.context.socket(zmq.SUB),
            "zmqpubrawblock": self.context.socket(zmq.SUB),
            "zmqpubsequence": self.context.socket(zmq.SUB),
            "zmqpubrawtx": self.context.socket(zmq.SUB),
            "zmqpubhashblock": self.context.socket(zmq.SUB)
        }
        
        self.addresses = {
            "zmqpubhashtx": "tcp://127.0.0.1:2936",
            "zmqpubrawblock": "tcp://127.0.0.1:2935",
            "zmqpubsequence": "tcp://127.0.0.1:2934",
            "zmqpubrawtx": "tcp://127.0.0.1:29332",
            "zmqpubhashblock": "tcp://127.0.0.1:29333"
        }
        
        self.callbacks = callbacks
        
        for key, socket in self.sockets.items():
            socket.connect(self.addresses[key])
            socket.setsockopt_string(zmq.SUBSCRIBE, '')
            socket.setsockopt(zmq.RCVTIMEO, 1000)  # Set a timeout of 1000ms (1 second)
        
        print("Listening for messages...")

    def listen(self):
        while True:
            try:
                for key, socket in self.sockets.items():
                    try:
                        # Receive the raw bytes message in non-blocking mode
                        message = socket.recv(flags=zmq.NOBLOCK)
                        if message == bytes("rawtx", "utf-8"):
                            #print(f"Received rawtx message on {key}")
                            # Receive the next message which is the raw transaction in hex
                            raw_tx_message = socket.recv(flags=zmq.NOBLOCK)
                            node_tx_index = socket.recv(flags=zmq.NOBLOCK)
                            self.callbacks[key](raw_tx_message, int.from_bytes(node_tx_index, byteorder='little'))
                        elif message == bytes("hashtx", "utf-8"):
                            #print(f"Received hashtx message on {key}")
                            # Receive the next message which is the raw transaction in hex
                            hashtx_message = socket.recv(flags=zmq.NOBLOCK)
                            node_tx_index = socket.recv(flags=zmq.NOBLOCK)
                            self.callbacks[key](hashtx_message, int.from_bytes(node_tx_index, byteorder='little'))
                        elif message == bytes("rawblock", "utf-8"):
                            #print(f"Received rawblock message on {key}")
                            # Receive the next message which is the raw block in hex
                            rawblock_message = socket.recv(flags=zmq.NOBLOCK)
                            node_block_index = socket.recv(flags=zmq.NOBLOCK)
                            self.callbacks[key](rawblock_message, int.from_bytes(node_block_index, byteorder='little'))
                        elif message == bytes("sequence", "utf-8"):
                            #print(f"Received sequence message on {key}")
                            # Receive the next message which is the sequence in hex
                            sequence_message = socket.recv(flags=zmq.NOBLOCK)
                            self.callbacks[key](sequence_message)
                        elif message == bytes("hashblock", "utf-8"):
                            #print(f"Received hashblock message on {key}")
                            # Receive the next message which is the hashblock in hex
                            hashblock_message = socket.recv(flags=zmq.NOBLOCK)
                            node_block_index = socket.recv(flags=zmq.NOBLOCK)
                            self.callbacks[key](hashblock_message, int.from_bytes(node_block_index, byteorder='little'))
                        else:
                            print(f"Received unknown message on {key}: {int.from_bytes(message, byteorder='little')}")
                            
                    except zmq.Again:
                        # No message was ready to be received
                        continue

            except Exception as e:
                print(f"Error receiving message: {e}")