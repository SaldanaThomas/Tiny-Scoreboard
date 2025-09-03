import os
import json
from tkinter import messagebox

# Recursively updates file paths in a dictionary or list
def update_file_paths(data, current_path):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = update_file_paths(value, current_path)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            data[i] = update_file_paths(item, current_path)
    elif isinstance(data, str) and 'x/' in data:
        # Replace the placeholder with the new path
        new_path = data.replace('x/', os.path.normpath(current_path) + os.sep)
        return new_path
    return data

# read JSON file, update paths, and save the new file
def update_json_paths():
    current_dir = os.getcwd()
    template_dir = os.path.join(current_dir, 'Template')
    json_file = os.path.join(template_dir, 'DO NOT TOUCH.json')
    output_file =  os.path.join(template_dir, 'Template.json')

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        updated_data = update_file_paths(json_data, current_dir)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_data, f, indent=4)

        messagebox.showinfo('JSON File Created', 'Template.json was successfully created and saved to Template directory')

    except FileNotFoundError:
       messagebox.showerror('Missing File', f'DO NOT TOUCH.json was not found in {os.path.join(current_dir, 'Template')} directory')
    except json.JSONDecodeError:
        messagebox.showerror('Wrong File Type', 'Could not decode JSON from DO NOT TOUCH.json. Please ensure it is a valid JSON file')
    except Exception as e:
        messagebox.showerror('Unknown Error', f'An unexpected error occurred: {e}')
