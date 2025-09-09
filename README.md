# My Python Program

This is a Python program that runs from the terminal. Follow the steps below to set it up and run.

```bash
# 1. Clone the repository
git clone https://github.com/AustralianSynchrotron/motionTestScript.git
cd myproject

# 2. Create a virtual environment
# Mac/Linux
python3 -m venv venv
source venv/bin/activate
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the program (replace myscript.py with your entry point)
python main.py

# 5. When done, deactivate the virtual environment
deactivate
