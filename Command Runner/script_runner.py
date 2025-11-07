import time
import argparse
import serial
import serial.tools.list_ports

def get_serial_port():
    """Gets the serial port from the user."""

    ports = serial.tools.list_ports.comports()

    if not ports:
        print("No serial ports found.")
        return None

    print("Available serial ports:")
    for i, port in enumerate(ports):
        print(f"{i + 1}. {port.device}")

    while True:
        try:
            choice = int(input("Select a port: "))
            if 1 <= choice <= len(ports):
                return ports[choice - 1].device
            else:
                print("Invalid choice. Please select a valid port.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def send_and_wait_for_response(ser, line, line_num = -1):
    ser.write(line.encode())

    while True:
        response = ser.readline().decode().strip()
        if response == "FIN":
            print(f"{line_num} | Command executed successfully.")
            break
        elif response == "ERR":
            print(f"{line_num} | Error executing command.")
            break

def custom_input_command(port:str):
    ser = serial.Serial(port, 9600, timeout=1)  # Replace with your serial port and baud rate
    while True:
        command = input("Enter command: ")
        print(f"{-1} | Sending: {command}")
        send_and_wait_for_response(ser, command)
        time.sleep(1)  # Adjust delay as needed

def run_program(port:str, file_path:str):
    line_num = 0
    ser = serial.Serial(port, 9600, timeout=1)  # Replace with your serial port and baud rate
    with open(file_path, 'r') as f:
        for line in f:
            line_num += 1
            line = line.strip()

            if (line == '' or line.startswith("%%")):
                continue

            if (line.startswith("END")):
                return

            print(f"{line_num} | Sending: {line}")
            send_and_wait_for_response(ser, line + '\n', line_num)
            time.sleep(1)  # Adjust delay as needed

if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str)
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            pass

    port = get_serial_port()
    if port:
        print(f"Selected port: {port}")
        # input("Press return to run program.")
        if args.file:
            run_program(port, args.file)
        else:
            custom_input_command(port)
    else:
        print(f"No port selected. Ending program.")
        exit
    