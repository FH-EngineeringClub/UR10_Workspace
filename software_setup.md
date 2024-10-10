# Software Setup Instructions

Follow these steps carefully to ensure all dependencies are installed correctly for this project.

## General Requirements

- **Python Version**: You will need Python 3.11

### Step 1: Verify Python Installation

1. **Check if Python is already installed**:

   - Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux).
   - Type the following command and press Enter:
     ```sh
     python --version
     ```
   - If Python is installed, you will see the version number. Ensure it is 3.9 or higher.

2. **If Python is not installed or the version is outdated**:
   - Download the installer from the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/).
   - Run the installer.
   - **Important**: During installation, make sure to check the box that says "Add Python to PATH".

### Step 2: Install Python Packages

1. **Create a Virtual Environment (Optional but Recommended)**:

   - In your project directory, run the following commands:
     ```sh
     python -m venv venv
     ```
   - Activate the virtual environment:
     - On **Windows**:
       ```sh
       .\venv\Scripts\activate
       ```
     - On **macOS/Linux**:
       ```sh
       source venv/bin/activate
       ```

2. **Install Required Packages**:
   - Make sure you are in the project directory where the `requirements.txt` file is located.
   - Run the following command to install all the required Python packages:
     ```sh
     pip install -r requirements.txt
     ```
   - If you encounter any issues installing `ur_rtde`, use the following command:
     ```sh
     pip install ur-rtde --use-pep517
     ```

## Stockfish Installation

### macOS

1. **Install Homebrew** (if not already installed):

   - Homebrew is a package manager for macOS. Open Terminal and run:
     ```sh
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
     ```
   - Follow the on-screen instructions to complete the installation.

2. **Install Stockfish**:
   - After Homebrew is installed, run:
     ```sh
     brew install stockfish
     ```

### Linux (Ubuntu 22.04 recommended)

1. **Download Stockfish**:

   - Open Terminal and run the following commands to download and extract Stockfish:
     ```sh
     wget https://stockfishchess.org/files/stockfish-ubuntu-x86-64.zip
     unzip stockfish-ubuntu-x86-64.zip
     ```

2. **Move Stockfish to a System Directory**:
   - Move the Stockfish binary to `/usr/bin` so that it can be accessed from anywhere:
     ```sh
     sudo mv stockfish-ubuntu-x86-64 /usr/bin/stockfish
     ```

### Windows

1. **Download Stockfish**:

   - Go to the Stockfish download page: [https://stockfishchess.org/download/](https://stockfishchess.org/download/).
   - Download the latest version of Stockfish for Windows.

2. **Add Stockfish to System PATH**:
   - Follow this guide to add Stockfish to your system PATH: [How to Add Executables to Your PATH in Windows](https://medium.com/@kevinmarkvi/how-to-add-executables-to-your-path-in-windows-5ffa4ce61a53).

## Additional Dependencies

### macOS

1. **Install CMake**:

   - Use Homebrew to install CMake:
     ```sh
     brew install cmake
     ```

2. **Install Boost Libraries**:

   - Run the following command:
     ```sh
     brew install boost
     ```

3. **Install Tkinter**:
   - Tkinter is required for graphical user interfaces. Install it using Homebrew:
     ```sh
     brew install tcl-tk
     ```
   - Add Tcl/Tk to your PATH by appending the following line to your `~/.zshrc` file:
     ```sh
     echo 'export PATH="/usr/local/opt/tcl-tk/bin:$PATH"' >> ~/.zshrc
     ```
   - Reload your shell configuration:
     ```sh
     source ~/.zshrc
     ```
   - Ensure Tcl/Tk is correctly added to your PATH:
     ```sh
     echo $PATH | grep --color=auto tcl-tk
     ```
   - Set environment variables for compilation:
     ```sh
     export LDFLAGS="-L/usr/local/opt/tcl-tk/lib"
     export CPPFLAGS="-I/usr/local/opt/tcl-tk/include"
     export PKG_CONFIG_PATH="/usr/local/opt/tcl-tk/lib/pkgconfig"
     ```
   - Test Tkinter installation:
     ```sh
     python -m tkinter -c "tkinter._test()"
     ```

### Linux (Ubuntu 22.04 recommended)

1. **Install Boost Libraries**:

   - Use the following command to install all Boost libraries:
     ```sh
     sudo apt-get install libboost-all-dev
     ```

2. **Install CMake**:

   - Install CMake using:
     ```sh
     sudo apt install cmake
     ```

3. **Install Tkinter**:

   - Install Tkinter for Python 3:
     ```sh
     sudo apt-get install python3-tk
     ```

4. **Install Additional Libraries**:
   - Install additional dependencies for RTDE (Real-Time Data Exchange):
     ```sh
     sudo apt-get install libusb-1.0-0-dev libudev-dev
     sudo apt-get update
     sudo apt install librtde librtde-dev
     ```

### Windows

1. **Install Boost**:

   - **Download Boost**:

     - Visit the Boost download page: [Boost download page](https://www.boost.org/users/download/).
     - Download the latest version (e.g., `boost_1_77_0.zip`).

   - **Extract Boost**:

     - Extract the ZIP file to a directory such as `C:\local\boost_1_77_0`.

   - **Set Environment Variables**:

     - Open the Start Menu, search for "Environment Variables", and select "Edit the system environment variables".
     - Click "Environment Variables" in the System Properties window.
     - Under "System variables", click "New" and add:
       - **Variable name:** `BOOST_ROOT`
       - **Variable value:** `C:\local\boost_1_77_0`
     - Click "OK" to save the new variable.

   - **Build Boost Libraries**:
     - Open Command Prompt as Administrator.
     - Navigate to the Boost directory:
       ```sh
       cd C:\local\boost_1_77_0
       ```
     - Run the bootstrap script:
       ```sh
       bootstrap.bat
       ```
     - Build the libraries:
       ```sh
       .\b2
       ```

2. **Install CMake**:

   - **Download CMake**:

     - Visit the [CMake download page](https://cmake.org/download/).
     - Download the Windows installer (e.g., `cmake-3.21.3-windows-x86_64.msi`).

   - **Install CMake**:

     - Run the installer and follow the prompts.
     - Ensure you select the option to "Add CMake to the system PATH for all users".

   - **Verify Installation**:
     - Open Command Prompt and check the installation:
       ```sh
       cmake --version
       ```
     - You should see the version number of CMake.

3. **Install Tkinter**:

   - Install Tkinter via pip:
     ```sh
     pip install tk
     ```
