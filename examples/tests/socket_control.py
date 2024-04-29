import socket
from time import sleep

HOST = "192.168.2.81"  # Replace with the IP address of your Universal Robot
PORT = 30002


def send_command_to_robot(command):
    # Connect to the robot
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    # Send the command to the robot
    sock.send(bytes(command, "utf-8"))

    # Receive and print the response from the robot
    response = sock.recv(1024)
    print("Response from robot:", response)

    # Close the connection
    sock.close()


# Call the function with the desired command
output_24 = "def myProg():\n\
    set_tool_voltage(24)\n\
end\n\
myProg()\n"

output_0 = "def myProg():\n\
    set_tool_voltage(0)\n\
end\n\
myProg()\n"

send_command_to_robot(output_0)
sleep(3)
send_command_to_robot(output_24)
