from chessviz import ChessViz

viz = ChessViz([[0,0], 400, 400], [[50, 50], 300, 300], cam_index=0)

# 0 - big crop
# 1 - small crop
viz.crop_gui(1)