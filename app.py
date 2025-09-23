import tkinter as tk
from tkinter import messagebox
from models.validation import ReportValidator
from models.classification import ReportRouter

def run_models():
    image_url = image_url_entry.get()
    description = description_entry.get("1.0", tk.END).strip()

    if not image_url or not description:
        messagebox.showerror("Input Error", "Please provide both image URL and description.")
        return

    # Initialize models
    validator = ReportValidator(image_url)
    router = ReportRouter("categories.json", "departments.json")

    # Validate the report
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "Validating...\n")
    is_valid = validator.validate(image_url, description)

    if is_valid:
        result_text.insert(tk.END, "\nValidation passed.\nClassifying...\n")
        assigned = router.classify_and_route(description)
        result_text.insert(tk.END, f"\nClassification Result:\n{assigned}")
    else:
        result_text.insert(tk.END, "\nValidation failed. Complaint is invalid.")

# Create main window
root = tk.Tk()
root.title("Civic Issue Report Validator & Classifier")
root.geometry("600x500")

# Image URL input
tk.Label(root, text="Image URL:").pack(pady=(10, 0))
image_url_entry = tk.Entry(root, width=80)
image_url_entry.pack(pady=(0, 10))

# Description input
tk.Label(root, text="Description:").pack()
description_entry = tk.Text(root, height=5, width=80)
description_entry.pack(pady=(0, 10))

# Run button
run_button = tk.Button(root, text="Validate & Classify", command=run_models)
run_button.pack(pady=10)

# Result display
tk.Label(root, text="Result:").pack()
result_text = tk.Text(root, height=15, width=80)
result_text.pack(pady=(0, 10))

root.mainloop()

