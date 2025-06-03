import tkinter as tk
import csv
import os
from datetime import datetime
from tkinter import filedialog, messagebox

# Get current year-month format
current_ym = datetime.now().strftime("%Y-%m")

class CSVProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EasyNodePro.com CSV Processor")
        self.root.geometry("550x350")
        
        # File path variables
        self.file_path = tk.StringVar()
        self.mapping_path = tk.StringVar()
        
        # Create UI elements
        tk.Label(root, text="Select CSV File:", font=('Arial', 12)).pack(pady=5)
        tk.Entry(root, textvariable=self.file_path, width=50).pack(padx=5)
        tk.Button(root, text="Select CSV", command=self.select_file, width=10).pack(pady=5)
        
        tk.Label(root, text="Find/Replace Mapping File:", font=('Arial', 12)).pack(pady=5)
        tk.Entry(root, textvariable=self.mapping_path, width=50).pack(padx=5)
        tk.Button(root, text="Select Mapping", command=self.select_mapping_file, width=15).pack(pady=5)
        
        tk.Button(root, text="Run", command=self.process_csv, 
                width=15, height=2, bg="lightblue").pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(root, text="", fg="green", font=('Arial', 10))
        self.status_label.pack(pady=5)

        # Auto-detect mapping file
        self.auto_detect_mapping()

    def auto_detect_mapping(self):
        """Check for mapping.csv in the same directory as app.py"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mapping_path = os.path.join(script_dir, 'mapping.csv')
        if os.path.exists(mapping_path):
            self.mapping_path.set(mapping_path)
            self.status_label.config(text="Auto-detected mapping.csv in same folder as app.py")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path.set(file_path)

    def select_mapping_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.mapping_path.set(file_path)

    def process_csv(self):
        input_path = self.file_path.get()
        mapping_path = self.mapping_path.get()

        if not input_path:
            messagebox.showerror("Error", "Please select a CSV file to process.")
            return

        # Read find/replace mapping
        replace_dict = {}
        if mapping_path:
            try:
                with open(mapping_path, 'r', newline='') as mapfile:
                    reader = csv.DictReader(mapfile)
                    if 'Find' not in reader.fieldnames or 'Replace' not in reader.fieldnames:
                        messagebox.showerror("Error", "Mapping file must have 'Find' and 'Replace' columns")
                        return
                    
                    for row in reader:
                        if row['Find']:  # Skip empty rows
                            replace_dict[row['Find']] = row['Replace']
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read mapping file: {str(e)}")
                return

        try:
            with open(input_path, 'r', newline='') as infile:
                reader = csv.reader(infile)
                rows = list(reader)
                
                if not rows:
                    messagebox.showerror("Error", "CSV file is empty.")
                    return
                
                header = rows[0]
                data_rows = rows[1:]

                # Apply address replacements
                for row in data_rows:
                    if row[0] in replace_dict:
                        row[0] = replace_dict[row[0]]

                # Split data into chunks of 797 rows each
                chunk_size = 797
                chunks = [data_rows[i:i + chunk_size] for i in range(0, len(data_rows), chunk_size)]

                # Create output directory
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_dir = os.path.join(os.path.dirname(input_path), f"{current_ym}/{base_name}_split")
                os.makedirs(output_dir, exist_ok=True)

                # Write chunks to files
                for i, chunk in enumerate(chunks):
                    output_path = os.path.join(output_dir, f"{base_name}_part_{i+1}.csv")
                    with open(output_path, 'w', newline='') as outfile:
                        writer = csv.writer(outfile)
                        writer.writerow(header)
                        writer.writerows(chunk)

                self.status_label.config(text=f"Success! Processed {len(data_rows)} records into {len(chunks)} files")
                messagebox.showinfo("Success", 
                                  f"Processed {len(data_rows)} records into {len(chunks)} files\nSaved in: {output_dir}")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVProcessorApp(root)
    root.mainloop()