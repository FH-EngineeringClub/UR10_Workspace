import rtde_io
import rtde_receive
# 192.168.2.81

rtde_io_ = rtde_io.RTDEIOInterface("192.168.2.81")
rtde_receive_ = rtde_receive.RTDEReceiveInterface("192.168.2.81")

# How-to set and get standard and tool digital outputs. Notice that we need the
# RTDEIOInterface for setting an output and RTDEReceiveInterface for getting the state
# of an output.
for x in range(0, 16):
    print(rtde_receive_.getDigitalOutState(x))
