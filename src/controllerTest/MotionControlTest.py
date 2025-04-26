from abc import ABC, abstractmethod

class MotionControlTest(ABC):
    """
    Abstract base class for motion control tests.
    """

    def __init__(self, test_name: str):
        self.test_name = test_name

    @abstractmethod
    def execute(self, motor: int, encoder: int):
        """
        Run the motion control test.
        """
        pass