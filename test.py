import serial.tools.list_ports

# Get an iterable of available serial ports
ports = serial.tools.list_ports.comports()

# Iterate through the ports and print their information
for port in ports:
    print(f"Device: {port.device}")
    print(f"Description: {port.description}")
    print(f"Hardware ID: {port.hwid}")
    print("-" * 20)