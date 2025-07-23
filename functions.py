import random
import string
import sqlite3
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet
from tkinter import ttk
import keyring


def show_login_screen(window, on_success_callback):
    """
    Opens the app and asks for password
    :param window: main window
    :param on_success_callback: function to call after entering a right password
    :return: nothing
    """
    service = "PasswordManager"
    username = "user"

    frame_login = tk.Frame(window)
    frame_login.pack(expand=True)

    # Determine if a password exists
    stored_password = keyring.get_password(service, username)
    is_new_password = stored_password is None

    if is_new_password:        # If it doesn't exist, create one
        title = "Create a password:"
        button_text = "Save Password"
    else:           # If it does, enter it
        title = "Enter password:"
        button_text = "Enter"

    title_label = tk.Label(frame_login, text=title)
    title_label.pack(pady=(20, 5))

    password_entry = tk.Entry(frame_login, show="*")
    password_entry.pack()

    def check_password():
        """
        Checks if the entered password is right
        :return: nothing
        """
        entered = password_entry.get()

        if is_new_password:        # Create password
            if not entered:        # Error if not entered
                messagebox.showerror("Error", "Please create a password")
                return
            # Password is saved, password list is open
            keyring.set_password(service, username, entered)
            messagebox.showinfo("Password Set", "Password has been saved")
            frame_login.destroy()
            on_success_callback()

        elif entered == stored_password:      # If entered password is right, open password list
            frame_login.destroy()
            on_success_callback()

        else:     # Error if password is wrong
            messagebox.showerror("Wrong Password", "Incorrect password")

    tk.Button(frame_login, text=button_text, command=check_password).pack(pady=10)


def build_password_list_ui(frame_list, show_generator_callback):
    """
    Creates password list ui
    :param frame_list: frame for list of passwords
    :param show_generator_callback: function to show password generator
    :return: nothing
    """
    # Half of page is a list of websites, other half is for details of a chosen site
    frame_left = tk.Frame(frame_list)
    frame_left.pack(side="left", fill="y", padx=10, pady=10)
    frame_right = tk.Frame(frame_list)
    frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    search_var = tk.StringVar()
    search_entry = tk.Entry(frame_left, textvariable=search_var)
    search_entry.pack(pady=(0, 5), padx=5, fill="x")

    listbox_container = tk.Frame(frame_left)
    listbox_container.pack(fill="both", expand=True, padx=5)
    listbox = tk.Listbox(listbox_container, height=12, width=30)
    listbox.pack(fill="both", expand=True)

    # "+" button opens generator page where a user can add new password
    add_button = ttk.Button(frame_left, text="+", command=show_generator_callback, width=1)
    add_button.pack(anchor="e", pady=5)

    details_label = tk.Label(frame_right, text="", justify="left", wraplength=240)
    details_label.pack(anchor="w", pady=2)

    delete_style = ttk.Style()
    delete_style.configure("Red.TButton", background="white", foreground="red")

    # A user can copy password or delete it, the buttons appear only after clicking on a website in list
    copy_button = ttk.Button(frame_right, text="Copy", width=4)
    delete_button = ttk.Button(frame_right, text="Delete", style="Red.TButton", width=5)
    copy_button.pack_forget()
    delete_button.pack_forget()

    # After clicking on a website, details about it are shown (login and password)
    listbox.bind("<<ListboxSelect>>", lambda event: on_site_select(frame_list, event, details_label, copy_button,
                                                                   delete_button))

    sites = []
    def refresh_listbox():
        """
        Refreshes websites list to instantly show new passwords in it
        :return: nothing
        """
        nonlocal sites
        # List is cleared before being refreshed
        listbox.delete(0, tk.END)
        conn = sqlite3.connect("passwords.db")
        cursor = conn.cursor()
        # All sites from passwords file appear in list
        cursor.execute("SELECT DISTINCT site FROM passwords")
        sites = [row[0] for row in cursor.fetchall()]
        conn.close()
        filter_sites()

    def filter_sites(*args):
        query = search_var.get().lower()
        listbox.delete(0, tk.END)
        for site in sites:
            if query in site.lower():
                listbox.insert(tk.END, site)

    search_var.trace_add("write", filter_sites)
    refresh_listbox()
    return refresh_listbox

def build_generator_ui(frame_generate, show_list_callback):
    """
    Creates password generator ui
    :param frame_generate: frame for generator
    :param show_list_callback: function to show list of passwords
    :return: nothing
    """

    website_label = tk.Label(frame_generate, text="Enter website name:")
    website_entry = tk.Entry(frame_generate)
    username_label = tk.Label(frame_generate, text="Enter username:")
    username_entry = tk.Entry(frame_generate)
    length_label = tk.Label(frame_generate, text="Enter length for the password:")
    length_entry = tk.Entry(frame_generate)

    # Generate
    password_label = ttk.Label(frame_generate, text="")
    generate_button = ttk.Button(frame_generate, text="Generate",
                                command=lambda: on_generate_click(frame_generate, website_entry, username_entry, length_entry,
                                                                  password_label))

    # Back button returns user to list page
    back_button = ttk.Button(frame_generate, text="Back", command=show_list_callback, width=4)

    back_button.pack(anchor="nw", padx=12, pady=12)
    website_label.pack()
    website_entry.pack()
    username_label.pack()
    username_entry.pack()
    length_label.pack()
    length_entry.pack()
    generate_button.pack()
    password_label.pack()


def generate_password(length, characters):
    """
    Generates password with at least one capital letter and a number
    :param length: length of password
    :param characters: list of characters that can be used
    :return: generated password
    """
    while True:
        password = ''.join(random.choice(characters) for _ in range(length))
        # Generate until there is at least one capital letter and a number
        if any(c.isalpha() for c in password) and any(c.isdigit() for c in password):
            break

    return password

def copy_to_clipboard(window, text):
    """
    Copies something to clipboard after clearing it
    :param window: window where the text is
    :param text: text we want to copy
    :return: nothing
    """
    window.clipboard_clear()
    window.clipboard_append(text)

def delete_item(listbox, details_label, copy_button, delete_button):
    """
    Deletes item from list including website name, username, and password
    :param listbox: list of items
    :param details_label: label that shows information about the item
    :param copy_button: button to copy password
    :param delete_button: button to delete password
    :return: nothing
    """
    selection = listbox.curselection()
    # If nothing is selected from list, nothing happens
    if not selection:
        return

    index = selection[0]
    site = listbox.get(index)

    # Ask for user's approval before deleting
    confirm = messagebox.askyesno("Confirm", f"Are you sure you want to delete password for {site}?")
    if not confirm:
        return

    # Delete from passwords file if user approved
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords WHERE site = ?", (site,))
    conn.commit()
    conn.close()

    # Delete from list
    listbox.delete(index)
    details_label.config(text="")

    # Copy and delete buttons disappear
    copy_button.pack_forget()
    delete_button.pack_forget()


def on_generate_click(window, website_entry, username_entry, length_entry, password_label):
    """
    After clicking on 'Generate' button, password is generated, printed, and copied
    :param window: The main window
    :param website_entry: website name
    :param username_entry: username
    :param length_entry: length of the password
    :param password_label: place to print password
    :return: final password
    """
    characters = string.ascii_letters + string.digits  # All letters and digits
    website = website_entry.get()
    username = username_entry.get()
    # Generating password
    length_str = length_entry.get()
    if not length_str.isdigit(): # Error if user didn't enter a number
        messagebox.showerror("Error", "Length must be a number")
        return

    length = int(length_str)

    password = generate_password(length, characters)
    password_label.config(text=password)

    # Copying password
    status_label = tk.Label(window, text="")
    copy_to_clipboard(window, password)
    status_label.config(text="Password copied")
    status_label.pack()
    window.after(2000, lambda: status_label.config(text=""))   # Message disappears

    # Saved to passwords file
    save_password(website, username, password)

    return password

def init_db():
    """
    Connect to .db file and create a table
    :return: nothing
    """
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()

    # Create a table with sites, usernames, and passwords
    cursor.execute("""CREATE TABLE IF NOT EXISTS passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        site TEXT,
        login TEXT,
        password TEXT)""")
    conn.commit()
    conn.close()

def save_password(website, username, password):
    """
    Add website, username, and password to the table
    :param website: website name
    :param username: username
    :param password: generated password
    :return: nothing
    """
    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()

    # Encrypt password
    encrypted = encrypt_password(password)

    cursor.execute("INSERT INTO passwords (site, login, password) VALUES (?, ?, ?)",
                   (website, username, encrypted))
    conn.commit()
    conn.close()


def on_site_select(window, event, details_label, copy_button, delete_button):
    """
    After clicking on a website name, shows username and password for it
    :param window: window of the program
    :param event: event that provokes calling the function
    :param details_label: place to print website login details
    :param copy_button: button to copy password
    :param delete_button: button to delete password
    :return: nothing
    """
    listbox = event.widget
    selection = listbox.curselection()
    if not selection:
        return
    index = selection[0]
    site = listbox.get(index)

    conn = sqlite3.connect("passwords.db")
    cursor = conn.cursor()

    # Assign login and password to their values
    cursor.execute("SELECT login, password FROM passwords WHERE site = ?", (site,))
    result = cursor.fetchone()
    login, password = result

    # Decrypt password
    encrypted = result[1]
    password = decrypt_password(encrypted)

    details_label.config(text=f"Website: {site}\nUsername: {login}\nPassword: {password}", anchor="w")
    # Add commands to copy and delete buttons and show them
    copy_button.config(command=lambda: copy_to_clipboard(window, password))
    delete_button.config(command=lambda: delete_item(listbox, details_label, copy_button, delete_button))
    copy_button.pack(anchor="w", pady=2)
    delete_button.pack(anchor="w", pady=2)

    conn.close()

def load_or_create_key():
    """
    loads a key or creates it if it doesn't exist
    :return: encoded key
    """
    service = "PasswordManager"
    key_name = "encryption_key"

    key = keyring.get_password(service, key_name)
    if key is None:
        key = Fernet.generate_key().decode()
        keyring.set_password(service, key_name, key)

    return key.encode()

def encrypt_password(password):
    """
    Encrypt password using a key
    :param password
    :return: encrypted password
    """
    key = load_or_create_key()
    fernet = Fernet(key)
    return fernet.encrypt(password.encode())

def decrypt_password(encrypted_password):
    """
    Decrypt password using a key
    :param encrypted_password
    :return: decrypted password
    """
    key = load_or_create_key()
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_password).decode()