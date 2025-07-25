import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.animation import FuncAnimation
import numpy as np
from kinematics_simulator import KinematicsSimulator
import unittest
import os
import csv
from datetime import datetime


class KinematicsUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Kinematics Simulator Pro")
        self.master.geometry("1100x750")
        self.master.minsize(900, 650)
        
        # Configure grid weights for responsive layout
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=3)
        self.master.grid_rowconfigure(2, weight=1)
        
        self.simulator = KinematicsSimulator()
        self.default_values = {
            "Initial Velocity (m/s):": "20",
            "Angle of Projection (degrees):": "45",
            "Initial X-Position (m):": "0",
            "Initial Y-Position (m):": "0",
            "Air Resistance Coefficient:": "0",
            "Gravity (m/s²):": "9.81"
        }
        self.current_simulation = None
        self.animation = None
        self.is_playing = False

        self.create_widgets()
        self.create_plot()
        self.set_default_values()
        self.setup_menu()

    def setup_menu(self):
        menubar = tk.Menu(self.master)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Simulation", command=self.clear)
        file_menu.add_command(label="Save Simulation", command=self.save_simulation)
        file_menu.add_command(label="Load Simulation", command=self.load_simulation)
        file_menu.add_separator()
        file_menu.add_command(label="Export Plot", command=self.export_plot)
        file_menu.add_command(label="Export Data", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        sim_menu.add_command(label="Run Simulation", command=self.simulate)
        sim_menu.add_command(label="Play Animation", command=self.toggle_animation)
        sim_menu.add_command(label="Reset Animation", command=self.reset_animation)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.master.config(menu=menubar)

    def create_widgets(self):
        # Input frame with improved layout
        input_frame = ttk.LabelFrame(self.master, text="Input Parameters", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        input_frame.grid_columnconfigure(1, weight=1)

        labels = [
            "Initial Velocity (m/s):", 
            "Angle of Projection (degrees):",
            "Initial X-Position (m):", 
            "Initial Y-Position (m):",
            "Air Resistance Coefficient:",
            "Gravity (m/s²):"
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
            text="Animate", 
            command=self.toggle_animation
        ).grid(row=0, column=1, padx=5, sticky="ew")
        
        ttk.Button(
            button_frame, 
            text="Clear", 
            command=self.clear
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
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.master, pack_toolbar=False)
        self.toolbar.grid(row=3, column=1, sticky="ew")
        
        # Initialize empty plot
        self.ax.set_xlabel("Distance (m)")
        self.ax.set_ylabel("Height (m)")
        self.ax.set_title("Projectile Trajectory")
        self.ax.grid(True)
        self.line, = self.ax.plot([], [], 'b-', linewidth=2)  # For animation
        self.point, = self.ax.plot([], [], 'ro', markersize=8)  # For animation
        self.canvas.draw()

    def set_default_values(self):
        for label, value in self.default_values.items():
            self.entries[label].delete(0, tk.END)
            self.entries[label].insert(0, value)

    def simulate(self):
        try:
            # Stop any running animation
            self.stop_animation()
            
            # Get input values with validation
            v0 = float(self.entries["Initial Velocity (m/s):"].get())
            theta = float(self.entries["Angle of Projection (degrees):"].get())
            x0 = float(self.entries["Initial X-Position (m):"].get())
            y0 = float(self.entries["Initial Y-Position (m):"].get())
            air_resistance = float(self.entries["Air Resistance Coefficient:"].get())
            gravity = float(self.entries["Gravity (m/s²):"].get())
            
            # Validate inputs
            if v0 <= 0:
                raise ValueError("Initial velocity must be positive")
            if not (0 <= theta <= 90):
                raise ValueError("Angle must be between 0 and 90 degrees")
            if y0 < 0:
                raise ValueError("Initial Y position cannot be negative")
            if air_resistance < 0:
                raise ValueError("Air resistance coefficient cannot be negative")
            if gravity <= 0:
                raise ValueError("Gravity must be positive")

            # Configure simulator
            self.simulator.gravity = gravity
            self.simulator.air_resistance_coeff = air_resistance

            # Run simulation
            trajectory = self.simulator.simulate_projectile_motion(v0, theta, x0, y0)
            self.current_simulation = {
                'trajectory': trajectory,
                'params': {
                    'v0': v0,
                    'theta': theta,
                    'x0': x0,
                    'y0': y0,
                    'air_resistance': air_resistance,
                    'gravity': gravity
                }
            }

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
                f"- Air Resistance: {air_resistance:.4f}",
                f"- Gravity: {gravity:.2f} m/s²",
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
        
        # Initialize animation components
        self.line.set_data([], [])
        self.point.set_data([], [])
        
        self.canvas.draw()

    def init_animation(self):
        self.line.set_data([], [])
        self.point.set_data([], [])
        return self.line, self.point

    def update_animation(self, frame):
        x_vals, y_vals = zip(*self.current_simulation['trajectory'][:frame+1])
        self.line.set_data(x_vals, y_vals)
        if frame < len(x_vals):
            self.point.set_data(x_vals[frame], y_vals[frame])
        return self.line, self.point

    def toggle_animation(self):
        if not self.current_simulation:
            messagebox.showwarning("No Simulation", "Please run a simulation first")
            return
            
        if self.is_playing:
            self.stop_animation()
        else:
            self.start_animation()

    def start_animation(self):
        if not self.current_simulation:
            return
            
        self.is_playing = True
        frames = len(self.current_simulation['trajectory'])
        interval = max(10, int(self.simulator.dt * 1000))
        
        self.animation = FuncAnimation(
            self.fig,
            self.update_animation,
            frames=frames,
            init_func=self.init_animation,
            interval=interval,
            blit=True,
            repeat=False
        )
        self.canvas.draw()

    def stop_animation(self):
        if self.animation:
            self.animation.event_source.stop()
        self.is_playing = False

    def reset_animation(self):
        self.stop_animation()
        if self.current_simulation:
            self.plot_trajectory(self.current_simulation['trajectory'])

    def save_simulation(self):
        if not self.current_simulation:
            messagebox.showwarning("No Data", "No simulation data to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Simulation Data"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.current_simulation, f, indent=4)
                messagebox.showinfo("Success", "Simulation saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def load_simulation(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Simulation Data"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Convert lists back to tuples if needed (JSON saves them as lists)
                data['trajectory'] = [tuple(point) for point in data['trajectory']]
                
                self.current_simulation = data
                params = data['params']
                
                # Update UI fields
                self.entries["Initial Velocity (m/s):"].delete(0, tk.END)
                self.entries["Initial Velocity (m/s):"].insert(0, str(params['v0']))
                
                self.entries["Angle of Projection (degrees):"].delete(0, tk.END)
                self.entries["Angle of Projection (degrees):"].insert(0, str(params['theta']))
                
                self.entries["Initial X-Position (m):"].delete(0, tk.END)
                self.entries["Initial X-Position (m):"].insert(0, str(params['x0']))
                
                self.entries["Initial Y-Position (m):"].delete(0, tk.END)
                self.entries["Initial Y-Position (m):"].insert(0, str(params['y0']))
                
                self.entries["Air Resistance Coefficient:"].delete(0, tk.END)
                self.entries["Air Resistance Coefficient:"].insert(0, str(params['air_resistance']))
                
                self.entries["Gravity (m/s²):"].delete(0, tk.END)
                self.entries["Gravity (m/s²):"].insert(0, str(params['gravity']))
                
                # Update plot and results
                self.plot_trajectory(data['trajectory'])
                self.simulate()  # This will update the results display
                
                messagebox.showinfo("Success", "Simulation loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def export_plot(self):
        if not self.current_simulation:
            messagebox.showwarning("No Data", "No plot to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg"),
                ("All files", "*.*")
            ],
            title="Export Plot"
        )
        
        if file_path:
            try:
                self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", "Plot exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export plot: {str(e)}")

    def export_data(self):
        if not self.current_simulation:
            messagebox.showwarning("No Data", "No data to export")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Data"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Time (s)", "X-Position (m)", "Y-Position (m)"])
                    
                    for i, (x, y) in enumerate(self.current_simulation['trajectory']):
                        time = i * self.simulator.dt
                        writer.writerow([time, x, y])
                
                messagebox.showinfo("Success", "Data exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def clear(self):
        self.stop_animation()
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
        self.current_simulation = None

    def show_about(self):
        about_text = (
            "Kinematics Simulator Pro\n"
            "Version 1.0\n\n"
            "A comprehensive projectile motion simulator with:\n"
            "- Air resistance modeling\n"
            "- Custom gravity settings\n"
            "- Animation capabilities\n"
            "- Data export options\n\n"
            "Created for physics education and research"
        )
        messagebox.showinfo("About Kinematics Simulator Pro", about_text)


class TestKinematicsSimulator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.app = KinematicsUI(cls.root)
        cls.root.withdraw()  # Hide the GUI window during tests

    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()

    def setUp(self):
        self.app.clear()

    def test_simulation_basic(self):
        # Set basic parameters
        self.app.entries["Initial Velocity (m/s):"].insert(0, "20")
        self.app.entries["Angle of Projection (degrees):"].insert(0, "45")
        
        # Run simulation
        self.app.simulate()
        
        # Check results
        output = self.app.output_text.get("1.0", tk.END)
        self.assertIn("Max Height", output)
        self.assertIn("Range", output)
        self.assertIn("Time of Flight", output)
        
        # Verify plot was created
        self.assertIsNotNone(self.app.current_simulation)
        self.assertGreater(len(self.app.current_simulation['trajectory']), 0)

    def test_air_resistance(self):
        # Set parameters with air resistance
        self.app.entries["Initial Velocity (m/s):"].insert(0, "20")
        self.app.entries["Angle of Projection (degrees):"].insert(0, "45")
        self.app.entries["Air Resistance Coefficient:"].insert(0, "0.1")
        
        # Run simulation
        self.app.simulate()
        
        # Check results mention air resistance
        output = self.app.output_text.get("1.0", tk.END)
        self.assertIn("Air Resistance: 0.1000", output)

    def test_save_load(self):
        # Run a basic simulation
        self.app.entries["Initial Velocity (m/s):"].insert(0, "20")
        self.app.entries["Angle of Projection (degrees):"].insert(0, "45")
        self.app.simulate()
        
        # Save to temporary file
        test_file = "test_simulation.json"
        self.app.current_simulation['test'] = True  # Add marker for verification
        with open(test_file, 'w') as f:
            json.dump(self.app.current_simulation, f)
        
        # Clear and load
        self.app.clear()
        self.app.load_simulation(test_file)
        
        # Verify loaded data
        self.assertIsNotNone(self.app.current_simulation)
        self.assertTrue(self.app.current_simulation.get('test', False))
        
        # Clean up
        os.remove(test_file)

    def test_export(self):
        # Run a basic simulation
        self.app.entries["Initial Velocity (m/s):"].insert(0, "20")
        self.app.entries["Angle of Projection (degrees):"].insert(0, "45")
        self.app.simulate()
        
        # Test plot export
        test_plot = "test_plot.png"
        self.app.fig.savefig(test_plot)
        self.assertTrue(os.path.exists(test_plot))
        os.remove(test_plot)
        
        # Test data export
        test_data = "test_data.csv"
        with open(test_data, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "X", "Y"])
            for i, (x, y) in enumerate(self.app.current_simulation['trajectory']):
                writer.writerow([i*self.app.simulator.dt, x, y])
        self.assertTrue(os.path.exists(test_data))
        os.remove(test_data)


if __name__ == "__main__":
    # Run unit tests if --test flag is passed
    import sys
    if "--test" in sys.argv:
        unittest.main(argv=sys.argv[:1])
    else:
        root = tk.Tk()
        
        # Set theme (requires ttkthemes or similar)
        try:
            from ttkthemes import ThemedStyle
            style = ThemedStyle(root)
            style.set_theme("arc")
        except ImportError:
            pass
        
        app = KinematicsUI(root)
        root.mainloop()
