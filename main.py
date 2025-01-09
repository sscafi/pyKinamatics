import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from kinematics_simulator import KinematicsSimulator  # import the simulator class

class KinematicsUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Kinematics Simulator")
        self.master.geometry("800x600")
        self.simulator = KinematicsSimulator()

        self.create_widgets()
        self.create_plot()

    def create_widgets(self):
        input_frame = ttk.LabelFrame(self.master, text="Input Parameters", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        labels = ["Initial Velocity (m/s):", "Angle of Projection (degrees):", 
                  "Initial X-Position (m):", "Initial Y-Position (m):"]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            self.entries[label] = ttk.Entry(input_frame, width=10)
            self.entries[label].grid(row=i, column=1, sticky="w", padx=5, pady=5)

        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=1, column=0, pady=10)

        ttk.Button(button_frame, text="Simulate", command=self.simulate).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Quit", command=self.master.quit).grid(row=0, column=2, padx=5)

        self.output_text = tk.Text(self.master, height=10, width=40)
        self.output_text.grid(row=2, column=0, padx=10, pady=10)

    def create_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=3, padx=10, pady=10)

    def simulate(self):
        try:
            v0 = float(self.entries["Initial Velocity (m/s):"].get())
            theta = float(self.entries["Angle of Projection (degrees):"].get())
            x0 = float(self.entries["Initial X-Position (m):"].get())
            y0 = float(self.entries["Initial Y-Position (m):"].get())

            trajectory = self.simulator.simulate_projectile_motion(v0, theta, x0, y0)

            self.output_text.delete(1.0, tk.END)
            max_height = max(y for _, y in trajectory)
            range_x = max(x for x, _ in trajectory) - x0
            time_of_flight = len(trajectory) * self.simulator.dt

            self.output_text.insert(tk.END, f"Max Height: {max_height:.2f} m\n")
            self.output_text.insert(tk.END, f"Range: {range_x:.2f} m\n")
            self.output_text.insert(tk.END, f"Time of Flight: {time_of_flight:.2f} s\n\n")
            self.output_text.insert(tk.END, "Trajectory (x, y):\n")
            for x, y in trajectory:
                self.output_text.insert(tk.END, f"({x:.2f}, {y:.2f})\n")

            self.plot_trajectory(trajectory)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for all fields.")

    def plot_trajectory(self, trajectory):
        self.ax.clear()
        x_vals, y_vals = zip(*trajectory)
        self.ax.plot(x_vals, y_vals)
        self.ax.set_xlabel("Distance (m)")
        self.ax.set_ylabel("Height (m)")
        self.ax.set_title("Projectile Trajectory")
        self.ax.grid(True)
        self.canvas.draw()

    def clear(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.output_text.delete(1.0, tk.END)
        self.ax.clear()
        self.ax.set_xlabel("Distance (m)")
        self.ax.set_ylabel("Height (m)")
        self.ax.set_title("Projectile Trajectory")
        self.ax.grid(True)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    ui = KinematicsUI(root)
    root.mainloop()
