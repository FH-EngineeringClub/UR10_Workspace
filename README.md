# UR10 Chess AI

Simple python script to test stockfish and python-chess.

## Instructions

- Install [stockfish](https://pypi.org/project/stockfish/) and [python-chess](https://pypi.org/project/chess/) with `pip install -r requirements.txt`

- Install the stockfish binary with `brew install stockfish` on macOS or by downloading [here](https://stockfishchess.org/download/) on windows

  - For linux, download the latest 64-bit version of stockfish [here](https://stockfishchess.org/download/linux/), open with `tar -xvf stockfish-ubuntu-x86-64.tar`, and place the binary in path with `mv stockfish-ubuntu-x86-64 /usr/bin/stockfish`
  - It may be helpful to add [stockfish to PATH](https://medium.com/@kevinmarkvi/how-to-add-executables-to-your-path-in-windows-5ffa4ce61a53) on windows

- Install [svg preview for VS code](https://marketplace.visualstudio.com/items?itemName=jock.svg)

- Preview chess.svg in VS code

- Run python_chess.py and input your move in SAN format (e.g. a2a4 or e2e4)

## [ur_rtde Installation](https://sdurobotics.gitlab.io/ur_rtde/installation/installation.html)

### Windows

[Install boost](https://www.geeksforgeeks.org/how-to-install-c-boost-libraries-on-windows/)  
[cmake](https://cmake.org/download/) may also be required  
`pip install ur-rtde --use-pep517`

### MacOS

`brew install cmake`  
`brew install boost`  
`pip install ur-rtde --use-pep517`

### Linux

`sudo apt-get install libboost-all-dev`  
`sudo add-apt-repository ppa:sdurobotics/ur-rtde`  
`sudo apt-get update`  
`sudo apt install librtde librtde-dev`  
`pip install ur-rtde --use-pep517`

## Resources

[UR Real-Time Communication Guide](https://www.universal-robots.com/articles/ur/interface-communication/real-time-data-exchange-rtde-guide/)

[UR Real-Time Communication Library Documentation](https://sdurobotics.gitlab.io/ur_rtde/index.html)
