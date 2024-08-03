import serial
import csv
import time
from datetime import datetime

# Serial port configuration
SERIAL_PORT = '/dev/ttyACM0'  # Adjust this if your Arduino is connected to a different port
BAUD_RATE = 9600

# CSV file configuration
CSV_FILE = 'arduino_data.csv'
CSV_HEADERS = ['Timestamp', 'Voltage', 'Current', 'Power', 'Servo Angle 1', 'Servo Angle 2', 
               'LDR Value 1', 'LDR Value 2', 'LDR Value 3', 'LDR Value 4']

def setup_serial():
    """Set up and return a serial connection."""
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"Connected to {SERIAL_PORT}")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def setup_csv():
    """Set up the CSV file with headers if it doesn't exist."""
    try:
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            file.seek(0, 2)  # Move to the end of the file
            if file.tell() == 0:  # File is empty, write headers
                writer.writerow(CSV_HEADERS)
        print(f"CSV file '{CSV_FILE}' is ready")
    except IOError as e:
        print(f"Error setting up CSV file: {e}")

def write_to_csv(data):
    """Append data to the CSV file."""
    try:
        with open(CSV_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
    except IOError as e:
        print(f"Error writing to CSV: {e}")

def main():
    ser = setup_serial()
    if not ser:
        return

    setup_csv()

    print("Listening for data...")
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    # Parse the data
                    data = line.split(',')
                    if len(data) == 9:  # Ensure we have all 9 fields
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        data_with_timestamp = [timestamp] + data
                        write_to_csv(data_with_timestamp)
                        print(f"Data received and saved: {data_with_timestamp}")
                    else:
                        print(f"Received incomplete data: {line}")
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
            # Try to reconnect
            ser.close()
            time.sleep(5)
            ser = setup_serial()
            if not ser:
                break
        except KeyboardInterrupt:
            print("Program terminated by user")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    if ser and ser.is_open:
        ser.close()
    print("Program ended")

if __name__ == "__main__":
    main()