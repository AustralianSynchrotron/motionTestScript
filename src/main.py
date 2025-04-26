from controllerTest import MotionControlResult, MoveTestAbsolute

def main():
    """
    Main function to run the move test.
    """
    # Example usage
    test = MoveTestAbsolute(test_name="Test 1", posn=2.0, precision=0.01)
    result = test.execute(motor=1, encoder=2)
    print(result)

if __name__ == "__main__":
    main()