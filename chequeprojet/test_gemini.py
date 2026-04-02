import os
import sys

# Add the project directory to sys.path so we can import users.utils
sys.path.append(os.getcwd())

try:
    from users.utils.gemini_extract import extract_cheque_info
    print("Successfully imported extract_cheque_info")
    
    # Test with a non-existent file to see if it catches the exception correctly
    result = extract_cheque_info("non_existent.jpg")
    print("Function call returned result (caught exception as expected)")
    print(result['message'])
except Exception as e:
    print(f"FAILED: {str(e)}")
