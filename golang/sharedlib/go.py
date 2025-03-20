import ctypes

# Load the shared library
golib = ctypes.CDLL("./golib.so")  # Use "golib.dll" on Windows

# Define the function signature
golib.HelloGo.restype = ctypes.c_char_p

# Call the function and capture the return value
result = golib.HelloGo().decode("utf-8")
print(result)  # Output: Hello from Go