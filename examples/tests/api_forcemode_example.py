import rtde_control

rtde_c = rtde_control.RTDEControlInterface("192.168.2.81")

task_frame = [0, 0, 0, 0, 0, 0]
selection_vector = [0, 0, 1, 0, 0, 0]
wrench_down = [0, 0, -35, 0, 0, 0]
wrench_up = [0, 0, 10, 0, 0, 0]
force_type = 2
limits = [0.1, 0.1, 0.01, 0.1, 0.1, 0.1]
dt = 1.0 / 500  # 2ms

# Execute 500Hz control loop for 4 seconds, each cycle is 2ms
# Execute 500Hz control loop for 4 seconds, each cycle is 2ms
for i in range(2000):
    t_start = rtde_c.initPeriod()
    # First move the robot down for 2 seconds, then up for 2 seconds
    if i > 1000:
        rtde_c.forceMode(task_frame, selection_vector, wrench_down, force_type, limits)
    else:
        rtde_c.forceMode(task_frame, selection_vector, wrench_up, force_type, limits)
    rtde_c.waitPeriod(t_start)

rtde_c.forceModeStop()
rtde_c.stopScript()
