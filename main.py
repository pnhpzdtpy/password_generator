
from functions import *
import tkinter as tk
import os

def main():

    # Create a database
    init_db()

    # Make a key
    if not os.path.exists("key.key"):
        load_or_create_key()

    # Create a window
    window = tk.Tk()
    window.geometry("600x300")
    window.minsize(600, 300)
    window.title("Password Manager")

    # List and generator pages
    frame_list = tk.Frame(window)
    frame_generate = tk.Frame(window)

    def show_password_generator():
        """
        Opens generator page
        :return: nothing
        """
        frame_list.pack_forget()
        frame_generate.pack(fill="both", expand=True)
        frame_generate.tkraise()
        frame_generate.update_idletasks()

    refresh_listbox = build_password_list_ui(frame_list, show_password_generator)

    def show_password_list():
        """
        Opens list page
        :return: nothing
        """
        frame_generate.pack_forget()
        frame_list.pack(fill="both", expand=True)
        frame_list.tkraise()
        frame_list.update_idletasks()
        refresh_listbox()

    build_generator_ui(frame_generate, show_password_list)

    show_login_screen(window, show_password_list)
    window.mainloop()

main()