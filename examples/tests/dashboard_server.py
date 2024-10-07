import socket

# Replace this IP with the IP of your robot or URSim instance
ROBOT_IP = "192.168.56.101"  # URSim or robot's IP address
DASHBOARD_PORT = 29999  # Dashboard Server port

# List of available Dashboard Server commands
COMMANDS = [
    "power on",
    "power off",
    "brake release",
    "load <program_path>",  # Replace <program_path> with the actual program path
    "play",
    "pause",
    "stop",
    "robotmode",
    "program state",
    "get loaded program",
    "unlock protective stop",
    "popup <message>",  # Replace <message> with your custom message
    "close popup",
    "safetystatus",
    "addToLog <message>",  # Replace <message> with the log entry
    "shutdown",
    "get serial number",
]


def connect_to_dashboard(robot_ip, port):
    """Establishes a connection to the Dashboard Server."""
    try:
        dashboard_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dashboard_socket.connect((robot_ip, port))
        print(f"Connected to Dashboard Server at {robot_ip}:{port}")
        return dashboard_socket
    except Exception as e:
        print(f"Error connecting to Dashboard Server: {e}")
        return None


def send_dashboard_command(socket_conn, command):
    """Sends a command to the Dashboard Server and retrieves the response."""
    try:
        socket_conn.sendall((command + "\n").encode())
        response = socket_conn.recv(1024).decode().strip()
        return response
    except Exception as e:
        return f"Error sending command: {e}"


def display_commands():
    """Displays the available commands to the user."""
    print("\nAvailable Commands:")
    for i, cmd in enumerate(COMMANDS, 1):
        print(f"{i}. {cmd}")


def main():
    # Connect to the Dashboard Server
    dashboard_socket = connect_to_dashboard(ROBOT_IP, DASHBOARD_PORT)
    if not dashboard_socket:
        return

    while True:
        # Display available commands
        display_commands()

        # Ask the user for input
        user_input = input(
            "\nEnter the number of the command you want to execute (or 'q' to quit): "
        ).strip()

        if user_input.lower() == "q":
            print("Exiting the dashboard command executor.")
            break

        try:
            # Validate the user input
            cmd_index = int(user_input) - 1
            if 0 <= cmd_index < len(COMMANDS):
                command = COMMANDS[cmd_index]

                # If command requires additional input, prompt the user
                if "<program_path>" in command:
                    program_path = input("Enter the program path to load: ").strip()
                    command = command.replace("<program_path>", program_path)
                elif "<message>" in command:
                    message = input("Enter the message to display or log: ").strip()
                    command = command.replace("<message>", message)

                # Send the command and display the response
                response = send_dashboard_command(dashboard_socket, command)
                print(f"Response: {response}")
            else:
                print("Invalid command number. Please try again.")

        except ValueError:
            print("Invalid input. Please enter a valid number.")

    # Close the connection
    dashboard_socket.close()
    print("Connection to Dashboard Server closed.")


if __name__ == "__main__":
    main()
