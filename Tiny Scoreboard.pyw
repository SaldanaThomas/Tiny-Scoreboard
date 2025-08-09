import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter import font as tkfont
import os
import sys

# --- New Imports ---
from country_data import country_map, country_names
from theme_data import themes, theme_colors

# ----------------------------
# Platform-specific Data Directory
# ----------------------------

def get_user_data_dir():
    """
    Returns the platform-specific user data directory for the application.
    This directory will be used for both the lock file and all data files.
    """
    if sys.platform == 'win32':
        # On Windows, use AppData/Local
        data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Tiny Scoreboard')
    elif sys.platform == 'darwin':  # macOS
        # On macOS, use Library/Application Support
        data_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'Tiny Scoreboard')
    else:  # Linux/Unix
        # On Linux, use .local/share
        data_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'tiny scoreboard')
    
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

# ----------------------------
# Instance Locking
# ----------------------------

try:
    user_data_dir = get_user_data_dir()
    lock_file_path = os.path.join(user_data_dir, 'lock.txt')
    
    lock_file = open(lock_file_path, 'w')
    
    if sys.platform == 'win32':
        import msvcrt
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    else:  # Unix-like systems
        import fcntl
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
except Exception:
    messagebox.showerror("Error", "Another instance of the application is already running.")
    sys.exit(1)

# ----------------------------
# Utility Functions
# ----------------------------

def remove_focus(event=None):
    """Remove focus from any widget (sets focus to root)."""
    root.focus_set()

def bind_enter_to_invoke(button):
    """Binds the Enter key to a button's command."""
    button.bind('<KeyPress-Return>', lambda e: (button.invoke(), 'break'))

# ----------------------------
# Path Configuration
# ----------------------------

PERSISTENT_DATA_DIR = user_data_dir
CONFIG_FILE = os.path.join(PERSISTENT_DATA_DIR, "config.txt")

def load_saved_path():
    """
    Load the saved backup path from config.txt.
    - If config.txt doesn't exist, create it with PERSISTENT_DATA_DIR.
    - If the stored path doesn't exist, fall back to PERSISTENT_DATA_DIR.
    """
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(PERSISTENT_DATA_DIR)
        return PERSISTENT_DATA_DIR

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        path = f.read().strip()
        return path if os.path.isdir(path) else PERSISTENT_DATA_DIR

backup_path = load_saved_path()

def save_path_to_config(new_path):
    """
    Save a new backup path to the config file and handle file transfers.
    - Copies .txt files from PERSISTENT_DATA_DIR to the new path, excluding
      config.txt and Theme.txt. - Cleans up old backup path if it's not PERSISTENT_DATA_DIR.
    """
    global backup_path

    new_path = os.path.abspath(new_path)
    os.makedirs(new_path, exist_ok=True)

    previous_backup_path = backup_path
    backup_path = new_path

    # Files to exclude from copying
    excluded_files = ["lock.txt", "config.txt", "Theme.txt", "PlayerList.txt"]

    # Copy files to new backup location
    if new_path != PERSISTENT_DATA_DIR:
        try:
            for filename in os.listdir(PERSISTENT_DATA_DIR):
                # Check if the file should be copied
                if filename.endswith(".txt") and filename not in excluded_files:
                    src = os.path.join(PERSISTENT_DATA_DIR, filename)
                    dst = os.path.join(new_path, filename)
                    try:
                        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
                            fdst.write(fsrc.read())
                    except Exception as e:
                        messagebox.showerror("Backup Error", f"Could not copy {filename}:\n{e}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Could not create backup:\n{e}")

    # Remove files from previous backup path
    if previous_backup_path != PERSISTENT_DATA_DIR and previous_backup_path != new_path:
        try:
            for filename in os.listdir(previous_backup_path):
                # Check if the file should be removed
                if filename.endswith(".txt") and filename not in excluded_files:
                    try:
                        os.remove(os.path.join(previous_backup_path, filename))
                    except Exception as e:
                        print(f"Error deleting {filename} from previous backup path:\n{e}")
        except Exception as e:
            print(f"Error accessing previous backup path for cleanup:\n{e}")

    # Save updated path to the config file (this file itself is not copied)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(backup_path)

# ----------------------------
# File Management
# ----------------------------

def update_file_paths():
    """Define file paths for all scoreboard elements."""
    global file_paths
    file_paths = {
        "Player 1": os.path.join(PERSISTENT_DATA_DIR, "Player1.txt"),
        "Player 2": os.path.join(PERSISTENT_DATA_DIR, "Player2.txt"),
        "Score 1": os.path.join(PERSISTENT_DATA_DIR, "Score1.txt"),
        "Score 2": os.path.join(PERSISTENT_DATA_DIR, "Score2.txt"),
        "Set": os.path.join(PERSISTENT_DATA_DIR, "Set.txt"),
        "Event": os.path.join(PERSISTENT_DATA_DIR, "Event.txt"),
        "Theme": os.path.join(PERSISTENT_DATA_DIR, "Theme.txt"),
        "Flag 1": os.path.join(PERSISTENT_DATA_DIR, "Flag1.txt"),
        "Flag 2": os.path.join(PERSISTENT_DATA_DIR, "Flag2.txt"),
        "PlayerList": os.path.join(PERSISTENT_DATA_DIR, "PlayerList.txt"),
    }

def initialize_files():
    """Create missing files with default values."""
    for label, path in file_paths.items():
        if not os.path.exists(path):
            with open(path, 'w', encoding='utf-8') as f:
                if "Score" in label:
                    f.write("0")
                elif label == "Theme":
                    f.write("Dark")
                else:
                    f.write("")  # Default empty value

update_file_paths()
initialize_files()

def save_to_file(label, value):
    """
    Save a value to the primary file and backup (if applicable).
    """
    # Exclude specific files from being saved to the backup path
    if label in ("Theme", "PlayerList"):
        # Save only to the primary file path
        primary_path = file_paths[label]
        with open(primary_path, 'w', encoding='utf-8') as f:
            f.write(str(value))
        return

    # Special handling for score files to write empty strings for empty values
    if "Score" in label:
        value_to_write = str(value) if value is not None and value != '' else ''
    else:
        value_to_write = str(value)
    
    # Save to primary file
    primary_path = file_paths[label]
    with open(primary_path, 'w', encoding='utf-8') as f:
        f.write(value_to_write)

    # Save to backup path if different from persistent data dir
    if backup_path != PERSISTENT_DATA_DIR:
        backup_file_path = os.path.join(backup_path, os.path.basename(primary_path))
        try:
            with open(backup_file_path, 'w', encoding='utf-8') as f:
                f.write(value_to_write)
        except Exception as e:
            messagebox.showerror("Backup Write Error", f"Failed to write backup for {label}:\n{e}")

# ----------------------------
# Autocomplete functionality
# ----------------------------

def load_player_list():
    """
    Loads player names from PlayerList.txt into a list. If the file doesn't exist, returns an empty list.
    """
    player_list_path = file_paths["PlayerList"]
    if not os.path.exists(player_list_path):
        return []
    with open(player_list_path, 'r', encoding='utf-8') as f:
        # Read lines, strip whitespace, ignore empty lines, and sort case-insensitively
        return sorted([line.strip() for line in f if line.strip()], key=str.lower)

PLAYER_LIST = load_player_list()

def autocomplete_entry_bind(entry, listbox, var, player_number):
    """Binds an Entry widget to an autocomplete Listbox with keyboard navigation and mouse support."""

    def on_key_press(event):
        # Handle Up and Down arrow keys for navigation
        if event.keysym in ("Down", "Up"):
            if listbox.winfo_ismapped():
                current_selection = listbox.curselection()

                if not current_selection:
                    # If no item is selected, navigate to the first or last item
                    if event.keysym == "Down":
                        next_idx = 0
                    else:  # Up arrow
                        next_idx = listbox.size() - 1
                else:
                    current_idx = current_selection[0]
                    if event.keysym == "Down":
                        if current_idx == listbox.size() - 1:
                            # Scroll off the bottom: clear selection and do nothing else
                            listbox.selection_clear(0, tk.END)
                            return "break"
                        next_idx = current_idx + 1
                    else:  # Up arrow
                        if current_idx == 0:
                            # Scroll off the top: clear selection and do nothing else
                            listbox.selection_clear(0, tk.END)
                            return "break"
                        next_idx = current_idx - 1
                
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(next_idx)
                listbox.activate(next_idx)
                listbox.see(next_idx)
            return "break"

    def on_key_release(event):
        """Handle key releases for both saving and autocomplete."""
        
        # Save the current text to the file on every key release
        save_to_file(f"Player {player_number}", var.get())
        
        if event.keysym in ("Down", "Up", "Return"):
            return

        text = var.get().lower()
        if not text:
            listbox.place_forget()
            return
        
        matches = [p for p in PLAYER_LIST if p.lower().startswith(text)][:3]
        
        if matches:
            listbox.delete(0, tk.END)
            for item in matches:
                listbox.insert(tk.END, item)
            
            x = entry.winfo_rootx() - root.winfo_rootx()
            y = entry.winfo_rooty() - root.winfo_rooty() + entry.winfo_height()
            listbox.place(x=x, y=y)
            
            listbox.selection_clear(0, tk.END)
            listbox.activate(0)
        else:
            listbox.place_forget()

    def on_select(event):
        """Called when a user clicks on a listbox item."""
        if listbox.curselection():
            selected_name = listbox.get(listbox.curselection())
            var.set(selected_name)
            listbox.place_forget()
            save_to_file(f"Player {player_number}", selected_name)
            remove_focus()

    def on_enter(event):
        """Handles the 'Return' key press."""
        if listbox.winfo_ismapped() and listbox.curselection():
            on_select(None)
        else:
            # Clear any selected text in the Entry widget before removing focus
            entry.selection_clear()
            remove_focus()

    def on_focus_out(event):
        """Clears selection on focus out and closes the listbox if another widget has focus."""
        entry.selection_clear()
        
        # Use a small delay to allow the focus change to fully register
        root.after(1, lambda: on_focus_out_check(event))

    def on_focus_out_check(event):
        """The actual check for the focus change."""
        new_focus_widget = root.focus_get()
        if new_focus_widget != listbox:
            listbox.place_forget()

    def on_hover(event):
        """Highlights a listbox item when the mouse hovers over it."""
        index = listbox.nearest(event.y)
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(index)
        listbox.activate(index)

    def on_leave(event):
        """Clears the selection when the mouse leaves the listbox."""
        listbox.selection_clear(0, tk.END)
        listbox.activate(tk.END)

    # Bindings
    entry.bind("<Key>", on_key_press)
    entry.bind("<KeyRelease>", on_key_release)
    entry.bind("<Return>", on_enter)
    entry.bind("<FocusOut>", on_focus_out)
    listbox.bind("<Button-1>", on_select)
    listbox.bind("<Motion>", on_hover)
    listbox.bind("<Leave>", on_leave)

# ----------------------------
# Constants
# ----------------------------

MIN_SCORE = 0
MAX_SCORE = 9999
hold_job = None
is_holding = False

# ----------------------------
# Tkinter Setup
# ----------------------------

root = tk.Tk()
root.title("Tiny Scoreboard")
root.resizable(False, False)

# Default font
default_font = tkfont.nametofont("TkDefaultFont")
default_font.configure(size=12)
root.option_add("*Font", default_font)

# Create a new font for the Combobox dropdown list
dropdown_font = tkfont.nametofont("TkDefaultFont").copy()
dropdown_font.configure(size=9)
root.option_add("*TCombobox*Listbox*Font", dropdown_font)


# Theme loading
try:
    with open(file_paths["Theme"], "r", encoding="utf-8") as f:
        saved_theme = f.read().strip()
    current_theme = tk.StringVar(
            value=saved_theme if saved_theme in ["Light", "Dark", "High Contrast", "Red", "Blue", "Green"]
            else "Dark"
        )
except FileNotFoundError:
    current_theme = tk.StringVar(value="Dark")

frame = ttk.Frame(root, padding=5)
frame.grid()


# ----------------------------
# Tkinter Variables
# ----------------------------

p1_var = tk.StringVar()
p2_var = tk.StringVar()
score1_var = tk.StringVar()
score2_var = tk.StringVar()
set_var = tk.StringVar()
event_var = tk.StringVar()
flag1_var = tk.StringVar()
flag2_var = tk.StringVar()


# ----------------------------
# Variable Loading
# ----------------------------

def load_var(var, label, cast=str):
    """
    Load a variable's value from its associated file.
    - cast: type to cast the file content to (str or int).
    """
    try:
        with open(file_paths[label], 'r', encoding='utf-8') as f:
            file_value = f.read().strip()
            # Special handling for flags to display the 2-character code directly
            if "Flag" in label:
                var.set(file_value)
            elif "Score" in label:
                # Load score as an empty string if the file is empty
                var.set(file_value if file_value else "")
            else:
                var.set(cast(file_value) if file_value else cast(0) if cast == int else "")
    except FileNotFoundError:
        var.set(cast(0) if cast == int else "")

def load_all_vars():
    """Load all scoreboard variables from their respective files."""
    load_var(p1_var, "Player 1")
    load_var(p2_var, "Player 2")
    load_var(score1_var, "Score 1")
    load_var(score2_var, "Score 2")
    load_var(set_var, "Set")
    load_var(event_var, "Event")
    load_var(flag1_var, "Flag 1")
    load_var(flag2_var, "Flag 2")

load_all_vars()

style = ttk.Style()
style.theme_use('clam')

try:
    style.element_create("Black.Vertical.Scrollbar.trough", "from", "clam")
except tk.TclError:
    pass

style.layout("Vertical.TScrollbar", [
    ("Vertical.Scrollbar.trough", {'sticky': 'ns'}),
    ("Vertical.Scrollbar.uparrow", {'side': 'top', 'sticky': ''}),
    ("Vertical.Scrollbar.downarrow", {'side': 'bottom', 'sticky': ''}),
    ("Vertical.Scrollbar.thumb", {'unit': '1', 'sticky': 'nswe'}),
])

def blend_color(hex1, hex2, ratio=0.5):
    """Blend two HEX colors together at a given ratio and brighten the result."""

    def hex_to_rgb(hex_code):
        return tuple(int(hex_code[i:i + 2], 16) for i in (1, 3, 5))

    def rgb_to_hex(rgb_tuple):
        return f"#{rgb_tuple[0]:02x}{rgb_tuple[1]:02x}{rgb_tuple[2]:02x}"

    def brighten(color_hex, ratio=0.2):
        white_rgb = (255, 255, 255)
        color_rgb = hex_to_rgb(color_hex)
        brightened_rgb = tuple(int(color_rgb[i] * (1 - ratio) + white_rgb[i] * ratio) for i in range(3))
        return rgb_to_hex(brightened_rgb)

    h1 = hex_to_rgb(hex1)
    h2 = hex_to_rgb(hex2)
    blended_rgb = tuple(int(h1[i] * (1 - ratio) + h2[i] * ratio) for i in range(3))
    blended_hex = rgb_to_hex(blended_rgb)

    return brighten(blended_hex)

def set_button_hover_effect(style, normal_bg, parent_bg):
    """Set button hover and focus background to 50% opacity blend."""
    hover_bg = blend_color(normal_bg, parent_bg, 0.5)
    style.map("TButton",
              background=[("active", hover_bg), ("focus", hover_bg)],
              relief=[("pressed", "sunken"), ("!pressed", "raised")])

def update_manage_players_listbox_theme():
    """Updates the colors of the Manage Players listbox based on the current theme."""
    if manage_players_win_instance and manage_players_win_instance.winfo_exists():
        entry_bg_color = style.lookup("TEntry", "fieldbackground")
        entry_fg_color = style.lookup("TEntry", "foreground")
        listbox_select_bg = style.lookup("TFrame", "background")
        listbox_select_fg = style.lookup("TFrame", "foreground")
        
        player_listbox.configure(
            bg=entry_bg_color,
            fg=entry_fg_color,
            selectbackground=listbox_select_bg,
            selectforeground=listbox_select_fg
        )

def apply_theme(theme_name):
    current_theme.set(theme_name)
    style = ttk.Style()
    style.theme_use('clam')

    style.configure("Vertical.TScrollbar",
                    background="white",
                    troughcolor="black",
                    bordercolor="black",
                    arrowcolor="white",
                    relief="flat",
                    gripcount=0)

    style.layout("Vertical.TScrollbar", [
        ("Vertical.Scrollbar.trough", {'sticky': 'ns'}),
        ("Vertical.Scrollbar.uparrow", {'side': 'top', 'sticky': ''}),
        ("Vertical.Scrollbar.downarrow", {'side': 'bottom', 'sticky': ''}),
        ("Vertical.Scrollbar.thumb", {'unit': '1', 'sticky': 'nswe'}),
    ])

    # Get the colors from the imported theme_colors dictionary
    colors = theme_colors.get(theme_name, theme_colors["Light"])

    style.configure(".", background=colors["bg"], foreground=colors["fg"], font=default_font)
    style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["entry_fg"], font=default_font)
    style.configure("TCombobox",
        fieldbackground=colors["entry_bg"],
        background=colors["entry_bg"],
        foreground=colors["entry_fg"],
        arrowcolor=colors["fg"],
        font=default_font)
    
    style.map("TCombobox",
        fieldbackground=[("readonly", colors["entry_bg"])],
        background=[("readonly", colors["entry_bg"])],
        foreground=[("readonly", colors["entry_fg"])],
        selectbackground=[("!focus", colors["entry_bg"])],
        selectforeground=[("!focus", colors["entry_fg"])]
    )

    style.configure("TButton", font=default_font, background=colors["btn_bg"])
    style.configure("TLabel", font=default_font)
    root.configure(bg=colors["bg"])
    
    style.configure("TCombobox.Popdown", font=dropdown_font)

    if theme_name != "Light":
        set_button_hover_effect(style, colors["btn_bg"], colors["bg"])
    else:
        set_button_hover_effect(style, colors["btn_bg"], "#888888")

    update_theme_checkmarks()
    save_to_file("Theme", theme_name)
    update_manage_players_listbox_theme()

def update_theme_checkmarks():
    for theme in themes:
        label = f"{theme} ✔" if current_theme.get() == theme else theme
        index = theme_menu_indices[theme]
        theme_submenu.entryconfig(index, label=label)

# --- MENU ---
menubar = tk.Menu(root)
settings_menu = tk.Menu(menubar, tearoff=0)

def show_file_location():
    if not backup_path or backup_path == PERSISTENT_DATA_DIR:
        messagebox.showinfo("File Location", "No Current File Location Set.\n\nSetting This Will Create Loose Files In Designated Location For All Input Fields.")
    else:
        messagebox.showinfo("File Location", f"Files Are Saved To:\n{backup_path}")

def choose_new_save_path():
    new_path = filedialog.askdirectory(initialdir=backup_path, title="Select Folder To Save Files")
    if new_path:
        save_path_to_config(new_path)
        messagebox.showinfo("Save Location Updated", f"New save path:\n{new_path}")

settings_menu.add_command(label="File Location", command=show_file_location)
settings_menu.add_command(label="Set File Location", command=choose_new_save_path)

# New "Manage Players" command
def save_player_list():
    """Saves the global PLAYER_LIST to the PlayerList.txt file."""
    player_list_path = file_paths["PlayerList"]
    with open(player_list_path, 'w', encoding='utf-8') as f:
        for player in PLAYER_LIST:
            f.write(player + '\n')

manage_players_win_instance = None
player_listbox = None # Global reference to the listbox

# Create a new font for the small text
small_font = tkfont.nametofont("TkDefaultFont").copy()
small_font.configure(size=9)

def manage_players_window():
    global manage_players_win_instance, player_listbox
    if manage_players_win_instance and manage_players_win_instance.winfo_exists():
        manage_players_win_instance.lift()
        return

    manage_players_win = tk.Toplevel(root)
    manage_players_win.title("Manage Players")
    manage_players_win.resizable(False, False)
    manage_players_win_instance = manage_players_win

    def on_close():
        global manage_players_win_instance, player_listbox
        manage_players_win_instance = None
        player_listbox = None
        manage_players_win.destroy()
    
    manage_players_win.protocol("WM_DELETE_WINDOW", on_close)

    frame = ttk.Frame(manage_players_win, padding=10)
    frame.pack(fill="both", expand=True)

    def update_listbox():
        player_listbox.delete(0, tk.END)
        for player in PLAYER_LIST:
            player_listbox.insert(tk.END, player)
    
    def add_player():
        player_name = add_player_entry.get().strip()
        if not player_name:
            return

        player_name_lower = player_name.lower()
        player_list_lower = [p.lower() for p in PLAYER_LIST]

        if player_name_lower in player_list_lower:
            index_to_replace = player_list_lower.index(player_name_lower)
            PLAYER_LIST[index_to_replace] = player_name
        else:
            PLAYER_LIST.append(player_name)

        PLAYER_LIST.sort(key=str.lower)
        update_listbox()
        save_player_list()
        add_player_entry.delete(0, tk.END)

    def remove_player(event=None):
        selected_indices = player_listbox.curselection()
        if selected_indices:
            index = selected_indices[0]
            player_to_remove = player_listbox.get(index)
            if player_to_remove in PLAYER_LIST:
                PLAYER_LIST.remove(player_to_remove)
                update_listbox()
                save_player_list()

    add_player_frame = ttk.Frame(frame)
    add_player_frame.pack(fill="x", pady=(0, 10))

    add_player_label = ttk.Label(add_player_frame, text="Add Player:")
    add_player_label.pack(side="left", padx=(0, 5))
    
    add_player_entry = ttk.Entry(add_player_frame)
    add_player_entry.pack(side="left", fill="x", expand=True)
    add_player_entry.bind("<Return>", lambda e: add_player())

    add_player_button = ttk.Button(add_player_frame, text="Add", command=add_player, width=5)
    add_player_button.pack(side="left", padx=(5, 0))
    bind_enter_to_invoke(add_player_button)

    # --- New Label for Autocomplete Info ---
    autocomplete_info_label = ttk.Label(frame, text="Added Players Become Auto Complete Options", font=small_font)
    autocomplete_info_label.pack(pady=(0, 10), anchor="center")
    # -------------------------------------

    listbox_frame = ttk.Frame(frame)
    listbox_frame.pack(fill="both", expand=True)

    player_listbox = tk.Listbox(
        listbox_frame,
        relief="flat",
        highlightthickness=0,
        activestyle="none"
    )
    player_listbox.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=player_listbox.yview)
    scrollbar.pack(side="right", fill="y")
    player_listbox.configure(yscrollcommand=scrollbar.set)
    
    update_manage_players_listbox_theme()
    update_listbox()
    
    remove_player_button = ttk.Button(frame, text="Remove Selected Player", command=remove_player)
    remove_player_button.pack(pady=(10, 0))
    player_listbox.bind("<Double-Button-1>", lambda e: None)
    bind_enter_to_invoke(remove_player_button)

settings_menu.add_command(label="Manage Players", command=manage_players_window)

theme_submenu = tk.Menu(settings_menu, tearoff=0)
settings_menu.add_cascade(label="Theme", menu=theme_submenu)
menubar.add_cascade(label="Settings", menu=settings_menu)
root.config(menu=menubar)

theme_menu_indices = {}
for idx, theme in enumerate(themes):
    theme_menu_indices[theme] = idx
    theme_submenu.add_command(label=theme, command=lambda t=theme: apply_theme(t))

apply_theme(current_theme.get())

# --- Variable Callbacks ---
def validate_score_input(new_value):
    if new_value == "":
        return True
    if len(new_value) > 4:
        return False
    try:
        val = int(new_value)
        return MIN_SCORE <= val <= MAX_SCORE
    except ValueError:
        return False

vcmd = (root.register(validate_score_input), "%P")

def update_score_file(var, label):
    """Saves the score value to the file, writing an empty string if the value is empty."""
    value = var.get()
    save_to_file(label, value)


# --- WIDGETS ---
# ROW 0
ttk.Label(frame, text="Event:").grid(column=0, row=0, sticky=tk.W, padx=(1, 0), pady=2)
event_entry = ttk.Entry(frame, textvariable=event_var, width=30)
event_entry.grid(column=1, row=0, padx=(2, 1), pady=2, ipady=5)
event_entry.bind("<KeyRelease>", lambda e: save_to_file("Event", event_var.get()))
event_entry.bind("<Return>", lambda e: remove_focus())
event_entry.bind("<FocusOut>", lambda e: event_entry.selection_clear())

ttk.Label(frame, text="Set:").grid(column=2, row=0, sticky=tk.W, padx=(2, 0), pady=2)
set_entry = ttk.Entry(frame, textvariable=set_var, width=33)
set_entry.grid(column=3, row=0, padx=(30, 1), pady=2, ipady=5, sticky=tk.W)
set_entry.bind("<KeyRelease>", lambda e: save_to_file("Set", set_var.get()))
set_entry.bind("<Return>", lambda e: remove_focus())
set_entry.bind("<FocusOut>", lambda e: set_entry.selection_clear())


# ROW 1
ttk.Label(frame, text="Player 1:").grid(column=0, row=1, sticky=tk.W, padx=1, pady=2)
p1_entry = ttk.Entry(frame, textvariable=p1_var, width=30)
p1_entry.grid(column=1, row=1, padx=(2, 1), pady=2, ipady=5)
p1_entry.bind("<Return>", lambda e: remove_focus())
p1_entry.bind("<FocusOut>", lambda e: p1_entry.selection_clear())

p1_listbox = tk.Listbox(root, height=3, width=39, font=('Arial', 10), relief="flat", highlightthickness=0)
p1_listbox.place_forget()
autocomplete_entry_bind(p1_entry, p1_listbox, p1_var, 1)

score_flags_1_frame = ttk.Frame(frame)
score_flags_1_frame.grid(column=2, row=1, columnspan=2, sticky=tk.W, padx=1, pady=1)

ttk.Label(score_flags_1_frame, text="Score 1:").grid(column=0, row=0, sticky=tk.W)
score1_box = ttk.Frame(score_flags_1_frame)
score1_box.grid(column=1, row=0, padx=(2, 0), sticky=tk.W)

score1_entry = ttk.Entry(score1_box, textvariable=score1_var, width=4, validate='key', validatecommand=vcmd)
score1_entry.grid(row=0, column=0, padx=1, sticky="ns")
score1_entry.bind("<KeyRelease>", lambda e: update_score_file(score1_var, "Score 1"))
score1_entry.bind("<Return>", lambda e: remove_focus())
score1_entry.bind("<FocusOut>", lambda e: score1_entry.selection_clear())

btn_up1 = ttk.Button(score1_box, text="▲", width=2)
btn_up1.grid(row=0, column=1, padx=1, sticky="ns")
btn_down1 = ttk.Button(score1_box, text="▼", width=2)
btn_down1.grid(row=0, column=2, padx=1, sticky="ns")

ttk.Label(score_flags_1_frame, text="Flag 1:").grid(column=2, row=0, sticky=tk.W, padx=(0, 1))
combo_flag1 = ttk.Combobox(score_flags_1_frame, textvariable=flag1_var, values=country_names, state='readonly', width=13)
combo_flag1.grid(column=3, row=0, padx=1, sticky="ns")

def highlight_top_option(event):
    """Highlights the top item (index 0) of the dropdown list when it's opened."""
    event.widget.configure(active=0)

combo_flag1.bind("<<ComboboxSelected>>", lambda e: (
    flag1_var.set(country_map.get(flag1_var.get(), "")),
    save_to_file("Flag 1", flag1_var.get()),
    remove_focus()
))
combo_flag1.bind("<<ComboboxPopdown>>", highlight_top_option)

# ROW 2
ttk.Label(frame, text="Player 2:").grid(column=0, row=2, sticky=tk.W, padx=1, pady=2)
p2_entry = ttk.Entry(frame, textvariable=p2_var, width=30)
p2_entry.grid(column=1, row=2, padx=(2, 1), pady=2, ipady=5)
p2_entry.bind("<Return>", lambda e: remove_focus())
p2_entry.bind("<FocusOut>", lambda e: p2_entry.selection_clear())

p2_listbox = tk.Listbox(root, height=3, width=39, font=('Arial', 10), relief="flat", highlightthickness=0)
p2_listbox.place_forget()
autocomplete_entry_bind(p2_entry, p2_listbox, p2_var, 2)

score_flags_2_frame = ttk.Frame(frame)
score_flags_2_frame.grid(column=2, row=2, columnspan=2, sticky=tk.W, padx=1, pady=1)

ttk.Label(score_flags_2_frame, text="Score 2:").grid(column=0, row=0, sticky=tk.W)
score2_box = ttk.Frame(score_flags_2_frame)
score2_box.grid(column=1, row=0, padx=(2, 0), sticky=tk.W)

score2_entry = ttk.Entry(score2_box, textvariable=score2_var, width=4, validate='key', validatecommand=vcmd)
score2_entry.grid(row=0, column=0, padx=1, sticky="ns")
score2_entry.bind("<KeyRelease>", lambda e: update_score_file(score2_var, "Score 2"))
score2_entry.bind("<Return>", lambda e: remove_focus())
score2_entry.bind("<FocusOut>", lambda e: score2_entry.selection_clear())

btn_up2 = ttk.Button(score2_box, text="▲", width=2)
btn_up2.grid(row=0, column=1, padx=1, sticky="ns")
btn_down2 = ttk.Button(score2_box, text="▼", width=2)
btn_down2.grid(row=0, column=2, padx=1, sticky="ns")

ttk.Label(score_flags_2_frame, text="Flag 2:").grid(column=2, row=0, sticky=tk.W, padx=(0, 1))
combo_flag2 = ttk.Combobox(score_flags_2_frame, textvariable=flag2_var, values=country_names, state='readonly', width=13)
combo_flag2.grid(column=3, row=0, padx=1, sticky="ns")
combo_flag2.bind("<<ComboboxSelected>>", lambda e: (
    flag2_var.set(country_map.get(flag2_var.get(), "")),
    save_to_file("Flag 2", flag2_var.get()),
    remove_focus()
))
combo_flag2.bind("<<ComboboxPopdown>>", highlight_top_option)

def increment_score(score_var, amount):
    current_value = score_var.get()
    if not current_value:
        if amount > 0:
            new_score = 1
        else:
            new_score = 0
    else:
        current_score = int(current_value)
        new_score = current_score + amount
    
    if MIN_SCORE <= new_score <= MAX_SCORE:
        score_var.set(str(new_score))
        save_to_file(f"Score {score_var.score_id}", new_score)

score1_var.score_id = 1
score2_var.score_id = 2

def start_increment_hold(score_var, amount, button):
    global hold_job, is_holding
    if not is_holding:
        is_holding = True
        increment_score(score_var, amount)
        hold_job = root.after(500, lambda: repeated_increment(score_var, amount, button))

def repeated_increment(score_var, amount, button):
    global hold_job
    increment_score(score_var, amount)
    hold_job = root.after(50, lambda: repeated_increment(score_var, amount, button))

def stop_hold(event):
    global hold_job, is_holding
    if hold_job and is_holding:
        root.after_cancel(hold_job)
        hold_job = None
        is_holding = False

# Mouse button bindings
btn_up1.bind("<ButtonPress-1>", lambda e: start_increment_hold(score1_var, 1, btn_up1))
btn_up1.bind("<ButtonRelease-1>", stop_hold)
btn_down1.bind("<ButtonPress-1>", lambda e: start_increment_hold(score1_var, -1, btn_down1))
btn_down1.bind("<ButtonRelease-1>", stop_hold)
btn_up2.bind("<ButtonPress-1>", lambda e: start_increment_hold(score2_var, 1, btn_up2))
btn_up2.bind("<ButtonRelease-1>", stop_hold)
btn_down2.bind("<ButtonPress-1>", lambda e: start_increment_hold(score2_var, -1, btn_down2))
btn_down2.bind("<ButtonRelease-1>", stop_hold)

# New global key bindings for continuous increment
def key_press_handler(event):
    global is_holding
    if event.keysym in ('Return', 'space') and not is_holding:
        focused_widget = root.focus_get()
        if focused_widget == btn_up1:
            start_increment_hold(score1_var, 1, btn_up1)
        elif focused_widget == btn_down1:
            start_increment_hold(score1_var, -1, btn_down1)
        elif focused_widget == btn_up2:
            start_increment_hold(score2_var, 1, btn_up2)
        elif focused_widget == btn_down2:
            start_increment_hold(score2_var, -1, btn_down2)

def key_release_handler(event):
    if event.keysym in ('Return', 'space'):
        stop_hold(event)

root.bind('<KeyPress>', key_press_handler)
root.bind('<KeyRelease>', key_release_handler)


# --- Button Functions ---
def swap_names():
    p1 = p1_var.get()
    p2 = p2_var.get()
    p1_var.set(p2)
    p2_var.set(p1)
    save_to_file("Player 1", p2)
    save_to_file("Player 2", p1)

def swap_scores():
    score1 = score1_var.get()
    score2 = score2_var.get()
    score1_var.set(score2)
    score2_var.set(score1)
    save_to_file("Score 1", score2)
    save_to_file("Score 2", score1)

def reset_names():
    p1_var.set("")
    p2_var.set("")
    save_to_file("Player 1", "")
    save_to_file("Player 2", "")

def reset_scores():
    score1_var.set("0")
    score2_var.set("0")
    save_to_file("Score 1", "0")
    save_to_file("Score 2", "0")

def reset_flags():
    flag1_var.set("")
    flag2_var.set("")
    save_to_file("Flag 1", "")
    save_to_file("Flag 2", "")

def reset_all():
    reset_names()
    reset_scores()
    reset_flags()
    set_var.set("")
    event_var.set("")
    save_to_file("Set", "")
    save_to_file("Event", "")

# --- Button Layout (ROW 3) ---
button_frame = ttk.Frame(frame)
button_frame.grid(column=0, row=3, columnspan=4, pady=(10, 0), sticky=tk.W+tk.E)

swap_names_btn = ttk.Button(button_frame, text="Swap Names", command=swap_names)
swap_scores_btn = ttk.Button(button_frame, text="Swap Scores", command=swap_scores)
reset_names_btn = ttk.Button(button_frame, text="Reset Names", command=reset_names)
reset_scores_btn = ttk.Button(button_frame, text="Reset Scores", command=reset_scores)
reset_all_btn = ttk.Button(button_frame, text="Reset All", command=reset_all)

swap_names_btn.grid(row=0, column=0, padx=2, pady=2, sticky=tk.W+tk.E)
swap_scores_btn.grid(row=0, column=1, padx=2, pady=2, sticky=tk.W+tk.E)
reset_names_btn.grid(row=0, column=2, padx=2, pady=2, sticky=tk.W+tk.E)
reset_scores_btn.grid(row=0, column=3, padx=2, pady=2, sticky=tk.W+tk.E)
reset_all_btn.grid(row=0, column=4, padx=2, pady=2, sticky=tk.W+tk.E)

button_frame.grid_columnconfigure(0, weight=1)
button_frame.grid_columnconfigure(1, weight=1)
button_frame.grid_columnconfigure(2, weight=1)
button_frame.grid_columnconfigure(3, weight=1)
button_frame.grid_columnconfigure(4, weight=1)

bind_enter_to_invoke(swap_names_btn)
bind_enter_to_invoke(swap_scores_btn)
bind_enter_to_invoke(reset_names_btn)
bind_enter_to_invoke(reset_scores_btn)
bind_enter_to_invoke(reset_all_btn)

def on_close():
    global lock_file
    if 'lock_file' in globals():
        if sys.platform == 'win32':
            import msvcrt
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_file.close()
        os.remove(lock_file_path)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()