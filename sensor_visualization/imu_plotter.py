#!/usr/bin/python3

import sys
import serial
import threading
import signal
import time
import numpy as np
from collections import deque
from PyQt5 import QtWidgets
import pyqtgraph as pg


#############################################
#           USER SETTINGS
#############################################

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE   = 115200
MAX_POINTS  = 500


#############################################
#  GLOBAL FLAGS + BUFFERS
#############################################

running = True          # <-- used by signal handler
ser = None              # serial object

acc_buffer = deque(maxlen=MAX_POINTS)
gyr_buffer = deque(maxlen=MAX_POINTS)
eul_buffer = deque(maxlen=MAX_POINTS)


#############################################
#        INTERRUPT HANDLER (CTRL+C)
#############################################

def handle_interrupt(sig, frame):
    global running, ser
    print("\n[INFO] Caught CTRL-C, shutting down...")

    running = False

    if ser and ser.is_open:
        try:
            ser.close()
            print("[INFO] Serial port closed.")
        except:
            pass

    # Close GUI if running
    QtWidgets.QApplication.quit()

# Register handler for Ctrl+C
signal.signal(signal.SIGINT, handle_interrupt)


#############################################
#        SERIAL READING THREAD
#############################################

def serial_reader():
    global ser, running
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print(f"[INFO] Connected to {SERIAL_PORT} at {BAUD_RATE}")
    except Exception as e:
        print("[ERROR] Could not open serial port:", e)
        running = False
        return

    while running:
        try:
            line = ser.readline().decode("utf-8").strip()
            if not line:
                continue

            parts = line.split(",")
            if len(parts) != 9:
                continue

            values = list(map(float, parts))
            ax, ay, az, gx, gy, gz, hd, pt, rl = values

            acc_buffer.append([ax, ay, az])
            gyr_buffer.append([gx, gy, gz])
            eul_buffer.append([hd, pt, rl])

        except Exception as e:
            # If user is exiting, ignore errors
            if running:
                print("Serial Error:", e)
            time.sleep(0.05)

    # cleanup when thread ends
    if ser and ser.is_open:
        ser.close()
        print("[INFO] Serial closed from thread.")


#############################################
#           MAIN PLOT WINDOW
#############################################

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time IMU Visualization")
        self.resize(1200, 900)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        # Acc plot
        self.acc_plot = pg.PlotWidget(title="Accelerometer (m/s²)")
        self.acc_plot.addLegend()
        layout.addWidget(self.acc_plot)

        self.acc_x = self.acc_plot.plot(pen='r', name="Acc X")
        self.acc_y = self.acc_plot.plot(pen='g', name="Acc Y")
        self.acc_z = self.acc_plot.plot(pen='b', name="Acc Z")

        # Gyro plot
        self.gyr_plot = pg.PlotWidget(title="Gyroscope (deg/s)")
        self.gyr_plot.addLegend()
        layout.addWidget(self.gyr_plot)

        self.gyr_x = self.gyr_plot.plot(pen='r', name="Gyr X")
        self.gyr_y = self.gyr_plot.plot(pen='g', name="Gyr Y")
        self.gyr_z = self.gyr_plot.plot(pen='b', name="Gyr Z")

        # Euler plot
        self.eul_plot = pg.PlotWidget(title="Euler Angles (deg)")
        self.eul_plot.addLegend()
        layout.addWidget(self.eul_plot)

        self.hd_plot = self.eul_plot.plot(pen='r', name="Heading")
        self.pt_plot = self.eul_plot.plot(pen='g', name="Pitch")
        self.rl_plot = self.eul_plot.plot(pen='b', name="Roll")

        # Update timer
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(20)  # update at 50 Hz

    def update_plots(self):
        if len(acc_buffer) > 5:
            acc = np.array(acc_buffer)
            self.acc_x.setData(acc[:, 0])
            self.acc_y.setData(acc[:, 1])
            self.acc_z.setData(acc[:, 2])

        if len(gyr_buffer) > 5:
            gyr = np.array(gyr_buffer)
            self.gyr_x.setData(gyr[:, 0])
            self.gyr_y.setData(gyr[:, 1])
            self.gyr_z.setData(gyr[:, 2])

        if len(eul_buffer) > 5:
            eul = np.array(eul_buffer)
            self.hd_plot.setData(eul[:, 0])
            self.pt_plot.setData(eul[:, 1])
            self.rl_plot.setData(eul[:, 2])


#############################################
#                    MAIN
#############################################

if __name__ == "__main__":
    # Start serial thread
    t = threading.Thread(target=serial_reader, daemon=True)
    t.start()

    # Start Qt GUI
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()

    # Run GUI until exit
    app.exec_()

    # Final cleanup after GUI closes
    running = False
    if ser and ser.is_open:
        ser.close()
        print("[INFO] Serial port closed on exit.")
