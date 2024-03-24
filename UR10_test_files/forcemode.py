import math
import rtde_control


HOSTNAME = "192.168.56.101"  # Replace with the IP address of your Universal Robot
HOST_PORT = 30002  # The port to send commands to the robot
RTDE_FREQUENCY = 10  # Hz to update from robot
control_interface = rtde_control.RTDEControlInterface(HOSTNAME, RTDE_FREQUENCY)

ANGLE = 44.785  # angle between the robot base and the chess board (in degrees)
DX = 401.34  # Home TCP position relative to base (in mm)
DY = -564.75

BOARD_HEIGHT = (
    0.09375
    + 0.03  # height of the board (in meters), measured as TCP Z relative to base
)
LIFT_HEIGHT = BOARD_HEIGHT + 0.254  # height of the lift (in meters)

TCP_RX = 2.2226  # rx (x rotation of TCP in radians)
TCP_RY = -2.2413  # ry (y rotation of TCP in radians)
TCP_RZ = 0.0489  # rz (z rotation of TCP in radians)

BIN_POSITION = {"x": 202.8, "y": -354.93}  # position to move to when not in use

MOVE_SPEED = 0.5  # speed of the tool [m/s]
MOVE_ACCEL = 0.3  # acceleration of the tool [m/s^2]

FORCE_SECONDS = 2  # duration of the force mode in seconds

task_frame = [
    0,
    0,
    0,
    0,
    0,
    0,
]  # A pose vector that defines the force frame relative to the base frame.
selection_vector = [
    0,
    0,
    1,
    0,
    0,
    0,
]  # A 6d vector that defines which degrees of freedom are controlled by the force/torque sensor.
tcp_down = [
    0,
    0,
    -0.1,  # -0.1 newton force in negative z direction (onto the piece)
    0,
    0,
    0,
]  # The force vector [x, y, z, rx, ry, rz] in the force frame.
FORCE_TYPE = 2  # The type of force to apply
limits = [2, 2, 1.5, 1, 1, 1]  # The tcp speed limits [x, y, z, rx, ry, rz]


def translate(x, y):
    """
    Rotate a point by a given angle in a 2d space
    """
    x1 = y * math.cos(ANGLE) - x * math.sin(ANGLE)
    y1 = y * math.sin(ANGLE) + x * math.cos(ANGLE)
    return x1 + DX, y1 + DY


def move_to_square(pos, height):
    robot_position = translate(pos["x"], pos["y"])
    control_interface.moveL(
        [
            robot_position[0] / 1000,  # x
            robot_position[1] / 1000,  # y
            height,  # z (height of the chess board)
            TCP_RX,  # rx (x rotation of TCP in radians)
            TCP_RY,  # ry (y rotation of TCP in radians)
            TCP_RZ,  # rz (z rotation of TCP in radians)
        ],
        MOVE_SPEED,  # speed: speed of the tool [m/s]
        MOVE_ACCEL,  # acceleration: acceleration of the tool [m/s^2]
    )


def forcemode_lower():
    for _ in range(
        RTDE_FREQUENCY * FORCE_SECONDS
    ):  # number of cycles to make (hz * duration in seconds)
        t_start = control_interface.initPeriod()
        # Move the robot down for 2 seconds
        control_interface.forceMode(
            task_frame, selection_vector, tcp_down, FORCE_TYPE, limits
        )
        control_interface.waitPeriod(t_start)

    control_interface.forceModeStop()


move_to_square({"x": 0, "y": 0}, BOARD_HEIGHT)
forcemode_lower()

# Execute 10Hz control loop for 2 seconds, each cycle is 100ms

# control_interface.stopScript()
