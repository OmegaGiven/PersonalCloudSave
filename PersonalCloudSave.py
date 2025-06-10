import os
import glob
import tkinter as tk
from tkinter import messagebox
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Authenticate Google Drive
def authenticate_drive():
    gauth = GoogleAuth()
    gauth.LoadClientConfigFile(".\client_secrets.json")  # Load JSON credentials
    gauth.LocalWebserverAuth()  # Open browser for authentication
    return GoogleDrive(gauth)


# Get all "My Games" directories
def find_game_saves():
    base_path = "C:\\Users\\*\\Documents\\My Games"
    game_dirs = glob.glob(base_path)
    return game_dirs

# Check if a folder exists, reuse it, or create a new one
def get_or_create_folder(drive, folder_name, parent_id=None):
    query = f"title = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    folder_list = drive.ListFile({'q': query}).GetList()
    if folder_list:
        return folder_list[0]['id']  # Folder exists, return its ID

    new_folder = drive.CreateFile({'title': folder_name, 'mimeType': 'application/vnd.google-apps.folder'})
    if parent_id:
        new_folder['parents'] = [{'id': parent_id}]
    new_folder.Upload()
    return new_folder['id']  # Return newly created folder ID

# Check if a file exists and if the local version is newer
def should_overwrite(drive, filename, parent_id, local_path):
    query = f"title = '{filename}' and '{parent_id}' in parents"
    file_list = drive.ListFile({'q': query}).GetList()

    if file_list:
        drive_file = file_list[0]  # Get existing file
        drive_modified = time.mktime(time.strptime(drive_file['modifiedDate'][:19], "%Y-%m-%dT%H:%M:%S"))
        local_modified = os.path.getmtime(local_path)

        return local_modified > drive_modified  # Upload only if the local file is newer
    return True  # If no file exists, upload it

# Upload files while maintaining hierarchy and updating only outdated files
def upload_selected():
    drive = authenticate_drive()
    selected_dirs = [dir_path for dir_path, var in check_vars.items() if var.get()]

    if not selected_dirs:
        messagebox.showwarning("Warning", "No directories selected!")
        return

    root_folder_id = get_or_create_folder(drive, "My Games")  # Create or reuse "My Games"

    folder_map = {}  # Track created folders to avoid duplicates

    for dir_path in selected_dirs:
        game_folder_name = os.path.basename(dir_path)
        game_folder_id = get_or_create_folder(drive, game_folder_name, root_folder_id)
        folder_map[dir_path] = game_folder_id

        for root_dir, _, files in os.walk(dir_path):  # Traverse subdirectories
            relative_path = os.path.relpath(root_dir, dir_path)  # Get relative path
            if relative_path != ".":
                sub_folder_id = folder_map.get(root_dir)
                if not sub_folder_id:
                    sub_folder_name = relative_path.replace("\\", "/")
                    sub_folder_id = get_or_create_folder(drive, sub_folder_name, game_folder_id)
                    folder_map[root_dir] = sub_folder_id

            # Upload files to the correct directory
            for filename in files:
                file_path = os.path.join(root_dir, filename)
                if should_overwrite(drive, filename, folder_map.get(root_dir, game_folder_id), file_path):
                    file_drive = drive.CreateFile({'title': filename, 'parents': [{'id': folder_map.get(root_dir, game_folder_id)}]})
                    file_drive.SetContentFile(file_path)
                    file_drive.Upload()
                    print(f"Uploaded (or updated): {file_path}")
                else:
                    print(f"Skipped (already up to date): {file_path}")

    messagebox.showinfo("Success", "Upload Complete!")


# UI Setup
root = tk.Tk()
root.title("Game Save Backup")

check_vars = {}
game_dirs = find_game_saves()

if not game_dirs:
    tk.Label(root, text="No game save directories found!").pack()
else:
    tk.Label(root, text="Select directories to upload:").pack()
    for dir_path in game_dirs:
        var = tk.BooleanVar()
        check_vars[dir_path] = var
        tk.Checkbutton(root, text=dir_path, variable=var).pack(anchor='w')

tk.Button(root, text="Upload Selected", command=upload_selected).pack()
root.mainloop()
