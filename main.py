import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from kinematics_simulator import KinematicsSimulator  # import the simulator class


class KinematicsUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Kinematics Simulator")
        self.master.geometry("1000x700")
        self.master.minsize(800, 600)
        
        # Configure grid weights for responsive layout
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=3)
        self.master.grid_rowconfigure(2, weight=1)
        
        self.simulator = KinematicsSimulator()
        self.default_values = {
            "Initial Velocity (m/s):": "20",
            "Angle of Projection (degrees):": "45",
            "Initial X-Position (m):": "0",
            "Initial Y-Position (m):": "0"
        }

        self.create_widgets()
        self.create_plot()
        self.set_default_values()

    def create_widgets(self):
        # Input frame with improved layout
        input_frame = ttk.LabelFrame(self.master, text="Input Parameters", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        input_frame.grid_columnconfigure(1, weight=1)

        labels = [
            "Initial Velocity (m/s):", 
            "Angle of Projection (degrees):",
            "Initial X-Position (m):", 
            "Initial Y-Position (m):"
        ]
        self.entries = {}

        for i, label in enumerate(labels):
            ttk.Label(input_frame, text=label).grid(
                row=i, column=0, sticky="e", padx=5, pady=5
            )
            self.entries[label] = ttk.Entry(input_frame, width=15)
            self.entries[label].grid(
                row=i, column=1, sticky="ew", padx=5, pady=5
            )

        # Button frame with improved buttons
        button_frame = ttk.Frame(self.master)
        button_frame.grid(row=1, column=0, pady=10, sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        ttk.Button(
            button_frame, 
            text="Simulate", 
            command=self.simulate,
            style="Accent.TButton"
        ).grid(row=0, column=0, padx=5, sticky="ew")
        
        ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear
        ).grid(row=0, column=1, padx=5, sticky="ew")
        
        ttk.Button(
            button_frame, 
            text="Quit", 
            command=self.master.quit
        ).grid(row=0, column=2, padx=5, sticky="ew")

        # Output text with scrollbar
        output_frame = ttk.LabelFrame(self.master, text="Simulation Results", padding="10")
        output_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        output_frame.grid_columnconfigure(0, weight=1)
        output_frame.grid_rowconfigure(0, weight=1)

        self.output_text = tk.Text(output_frame, height=10, wrap=tk.NONE)
        self.output_text.grid(row=0, column=0, sticky="nsew")

        scroll_y = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        scroll_y.grid(row=0, column=1, sticky="ns")
        self.output_text.configure(yscrollcommand=scroll_y.set)

        scroll_x = ttk.Scrollbar(output_frame, orient="horizontal", command=self.output_text.xview)
        scroll_x.grid(row=1, column=0, sticky="ew")
        self.output_text.configure(xscrollcommand=scroll_x.set)

    def create_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().grid(
            row=0, column=1, rowspan=3, padx=10, pady=10, sticky="nsew"
        )
        
        # Add matplotlib navigation toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
        toolbar.grid(row=3, column=1, sticky="ew")
        
        # Initialize empty plot
        self.ax.set_xlabel("Distance (m)")
        self.ax.set_ylabel("Height (m)")
        self.ax.set_title("Projectile Trajectory")
        self.ax.grid(True)
        self.canvas.draw()

    def set_default_values(self):
        for label, value in self.default_values.items():
            self.entries[label].insert(0, value)

    def simulate(self):
        try:
            # Get input values with validation
            v0 = float(self.entries["Initial Velocity (m/s):"].get())
            theta = float(self.entries["Angle of Projection (degrees):"].get())
            x0 = float(self.entries["Initial X-Position (m):"].get())
            y0 = float(self.entries["Initial Y-Position (m):"].get())
            
            # Validate inputs
            if v0 <= 0:
                raise ValueError("Initial velocity must be positive")
            if not (0 <= theta <= 90):
                raise ValueError("Angle must be between 0 and 90 degrees")
            if y0 < 0:
                raise ValueError("Initial Y position cannot be negative")

            # Run simulation
            trajectory = self.simulator.simulate_projectile_motion(v0, theta, x0, y0)

            # Calculate and display results
            self.output_text.delete(1.0, tk.END)
            y_values = [y for _, y in trajectory]
            x_values = [x for x, _ in trajectory]
            
            max_height = max(y_values)
            range_x = max(x_values) - x0
            time_of_flight = len(trajectory) * self.simulator.dt

            results = [
                f"Simulation Parameters:",
                f"- Initial Velocity: {v0:.2f} m/s",
                f"- Projection Angle: {theta:.2f}°",
                f"- Initial Position: ({x0:.2f}, {y0:.2f}) m",
                "\nResults:",
                f"- Max Height: {max_height:.2f} m",
                f"- Range: {range_x:.2f} m",
                f"- Time of Flight: {time_of_flight:.2f} s",
                "\nTrajectory (first 10 points):"
            ]
            
            self.output_text.insert(tk.END, "\n".join(results) + "\n")
            for x, y in trajectory[:10]:
                self.output_text.insert(tk.END, f"({x:.2f}, {y:.2f})\n")
            
            if len(trajectory) > 10:
                self.output_text.insert(tk.END, f"\n... and {len(trajectory)-10} more points")

            self.plot_trajectory(trajectory)

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def plot_trajectory(self, trajectory):
        self.ax.clear()
        x_vals, y_vals = zip(*trajectory)
        
        # Enhanced plot with markers and styling
        self.ax.plot(
            x_vals, y_vals, 
            'b-',  # blue solid line
            linewidth=2,
            marker='o', 
            markersize=4,
            markerfacecolor='red',
            markevery=int(len(x_vals)/10) or 1  # show ~10 markers
        )
        
        # Mark important points
        self.ax.plot(
            x_vals[0], y_vals[0], 
            'go',  # green dot for start
            markersize=8,
            label='Start'
        )
        
        self.ax.plot(
            x_vals[-1], y_vals[-1], 
            'ro',  # red dot for end
            markersize=8,
            label='Landing'
        )
        
        max_idx = y_vals.index(max(y_vals))
        self.ax.plot(
            x_vals[max_idx], y_vals[max_idx], 
            'yo',  # yellow dot for max height
            markersize=8,
            label='Max Height'
        )
        
        self.ax.set_xlabel("Distance (m)")
        self.ax.set_ylabel("Height (m)")
        self.ax.set_title("Projectile Trajectory")
        self.ax.grid(True, linestyle='--', alpha=0.7)
        self.ax.legend()
        
        # Set equal aspect ratio if x and y scales are similar
        x_range = max(x_vals) - min(x_vals)
        y_range = max(y_vals) - min(y_vals)
        if 0.5 < x_range/y_range < 2:
            self.ax.set_aspect('equal', adjustable='box')
        
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
        self.set_default_values()


if __name__ == "__main__":
    root = tk.Tk()
    
    # Set theme (requires ttkthemes or similar)
    try:
        from ttkthemes import ThemedStyle
        style = ThemedStyle(root)
        style.set_theme("arc")
    except ImportError:
        pass
    
    ui = KinematicsUI(root)
    root.mainloop()
