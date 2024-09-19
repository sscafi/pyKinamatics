# Kinematics Simulator UI
# ======================

import tkinter as tk
from kinematics_simulator import KinematicsSimulator  # import the simulator class

class KinematicsUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Kinematics Simulator")
        self.simulator = KinematicsSimulator()

        # Create input fields
        self.v0_label = tk.Label(master, text="Initial Velocity (m/s):")
        self.v0_label.grid(row=0, column=0)
        self.v0_entry = tk.Entry(master)
        self.v0_entry.grid(row=0, column=1)

        self.theta_label = tk.Label(master, text="Angle of Projection (degrees):")
        self.theta_label.grid(row=1, column=0)
        self.theta_entry = tk.Entry(master)
        self.theta_entry.grid(row=1, column=1)

        self.x0_label = tk.Label(master, text="Initial X-Position (m):")
        self.x0_label.grid(row=2, column=0)
        self.x0_entry = tk.Entry(master)
        self.x0_entry.grid(row=2, column=1)

        self.y0_label = tk.Label(master, text="Initial Y-Position (m):")
        self.y0_label.grid(row=3, column=0)
        self.y0_entry = tk.Entry(master)
        self.y0_entry.grid(row=3, column=1)

        # Create buttons
        self.simulate_button = tk.Button(master, text="Simulate", command=self.simulate)
        self.simulate_button.grid(row=4, column=0, columnspan=2)

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.grid(row=5, column=0, columnspan=2)

        # Create output field
        self.output_text = tk.Text(master, height=10, width=40)
        self.output_text.grid(row=6, column=0, columnspan=2)

    def simulate(self):
        # Get input values
        v0 = float(self.v0_entry.get())
        theta = float(self.theta_entry.get())
        x0 = float(self.x0_entry.get())
        y0 = float(self.y0_entry.get())

        # Simulate projectile motion
        trajectory = self.simulator.simulate_projectile_motion(v0, theta, x0, y0)

        # Display output
        self.output_text.delete(1.0, tk.END)
        for x, y in trajectory:
            self.output_text.insert(tk.END, f"({x:.2f}, {y:.2f})\n")

root = tk.Tk()
ui = KinematicsUI(root)
root.mainloop()