# Motion Test Script

This is a Python program that runs from the terminal. Follow the steps below to set it up and run.

# Running the script

Need to modify according to ANSTO laptop security requirements.

## 1. Clone the repository
```bash
git clone https://github.com/AustralianSynchrotron/motionTestScript.git
cd myproject
```

## 2. Create a virtual environment
```bash
# Mac/Linux
python3 -m venv venv
source venv/bin/activate
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Configure your the tests to run in main.py in the main() function.

## 5. Run the program
```bash
python main.py
```

## 6. When done, deactivate the virtual environment
```bash
deactivate
```

# How the script works

## Script Structure

### Controller

The controller class is in charge of the communication with the Motion Controller.

This class is where the low-level functionality is handled, as well as higher level functions, such as getting position, setting velocity and starting a gather.

Custom commands can be run through the custom_command_non_blocking and custom_command_blocking functions.

*This class can be improved by creating an abstract class that concrete controllers can inherit, meaning controllers can be changed interchangeably with the tests.

### Controller Test

The Motion Control Test class is an abstract class with two concrete methods - main_execution and visualise_gather_data - and one abstract method execute.

The main_execution method is a wrapper of the abstract execute command and is in charge of the timeout and starting the gather data during the test. The gather data files are saved into the results folder each with a unique id (the id can be found in the test report).

The visualise_gather_data method is in charge of graphing the gather data using matplotlib. The visualised data is saved into the results folder with a unique id.

The execute method is an abstract method that the concrete test classes implement. In the concrete test classes - LimitTest, MoveTestAbsolute, MoveTestRelative, OvershootTest, RepeatabilityTest & VelocityTest - they implement their specific execution logic for the test. Each execute method must return a MotionControlResult.

*These tests should be updated to do test validation using the gather data, rather than the SSH commands to get a high enough sampling to ensure precise and reliable results.

*An test_initialisation function should be introduced to set the starting parameters of a test, to ensure consistency with testing.

### Report Generator

The report generator class takes in a list of MotionControlResults and then generates a motion control report file in the results folder.

### Main Execution

The main.py file contains the following methods: main and tests_to_run.

The main method is where the controller connection is established and where the tests are executed, results are saved and reports are generated. The start of the method requires the following details:

* host_ip - the IP of the motion control system.
* motor - the channel number of the motor being tested.
* encoder - the channel number of the enocder being tested.
* gather_data - either True or False whether you want to gather data.
* gather_data_items - an array of items/attributes to be collected in gather. Ensure each item is suffixed with a ".a" to reference the attribute address.
* timeout - the amount of time in seconds before a test should fail.
* run_id - the run id for the test suite.

The tests_to_run method is where the suite of tests you want to test are defined. They are all added to a tests list. This method is called by the main method to get these list of tests.