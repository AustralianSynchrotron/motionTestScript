from abc import ABC, abstractmethod
from controller import Controller

class MotionControlTest(ABC):
    """
    Abstract base class for motion control tests.
    """

    def __init__(self, test_name: str, generic_name: str, controller: Controller):
        self.test_name = test_name
        self.generic_name = generic_name
        self.controller = controller

    @abstractmethod
    def execute(self, motor: int, encoder: int):
        """
        Run the motion control test.
        """
        pass