import pickle
import tkinter as tk
from tkinter import messagebox, simpledialog
from regStuff import RegistrySetter
from client_constants import *
from pServer import main
from elevate import elevate
import ctypes
from client_protocol import Protocol

"""
Name: GUI
Author: Roee Dassa
Explanation: graphic user interface so the
user can interact with code intuitively
"""


class LoginSignUpGUI:
    def __init__(self, root):
        # Initialize the GUI window
        self.root = root
        self.root.title("Login/Signup GUI")
        root.geometry("500x300")  # Increase the window size

        # Create and pack GUI elements (labels, entries, buttons)
        self.username_label = tk.Label(root, text="Username:", width=30,
                                       height=2, font=("Arial", 12))
        self.username_label.pack()

        self.username_entry = tk.Entry(root, width=50)
        self.username_entry.pack()

        self.password_label = tk.Label(root, text="Password:", width=30,
                                       height=2, font=("Arial", 12))
        self.password_label.pack()

        self.password_entry = tk.Entry(root, show="*", width=50)
        self.password_entry.pack()

        self.choice_label = tk.Label(root, text="Choose an option:",
                                     font=("Arial", 12))
        self.choice_label.pack()

        self.login_button = tk.Button(root, text="Login", width=10, height=1,
                                      font=("Arial", 12),
                                      command=self.login)
        self.login_button.pack()

        self.signup_button = tk.Button(root, text="Signup", width=10,
                                       height=1,
                                       font=("Arial", 12),
                                       command=self.signup)
        self.signup_button.pack()

        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

        self.server_address = (BIG_SERVER_IP_CLIENT, BIG_SERVER_PORT)

    def signup(self):
        # Function to handle signup button click
        self.status_label.config(text="")
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        # Save the username in the Windows Registry
        # under HKEY_LOCAL_MACHINE\SOFTWARE\CVSM
        data = self.username
        RegistrySetter.create_reg(data)

        # Send signup request to bigServer
        signup_success = self.send_request({'action': 'signup',
                                            'username': self.username,
                                            'password': self.password})

        if signup_success == "OK":
            self.status_label.config(text="Signup successful!")

        elif signup_success == "NO":
            self.status_label.config(text="Signup failed. "
                                          "Make sure password"
                                          "is at least 8 characters"
                                          "long, contains letters, numbers"
                                          "and special characters.")
        self.root.destroy()
        main()
        RegistrySetter.create_running_reg(bat_file_path)

    def login(self):
        # Function to handle login button click
        self.status_label.config(text="")
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        # Send login request to bigServer
        login_success = self.send_request({'action': 'login',
                                           'username': self.username,
                                           'password': self.password})

        if login_success == "OK":
            # If the user logs in properly, forward
            # them to next possible actions (view / add / remove)
            self.display_options()

        elif login_success == "NO":
            self.status_label.config(text="Login failed. "
                                          "Please enter correct "
                                          "user data.")

        else:
            self.status_label.config(text="Encountered unknown "
                                          "error")

    def display_options(self):
        self.login_button.destroy()
        self.signup_button.destroy()

        self.view_sites_button = tk.Button(self.root,
                                           text="View Banned Sites",
                                           width=20, height=2,
                                           font=("Arial", 12),
                                           command=self.view_banned_sites)
        self.view_sites_button.pack()

        self.add_site_button = tk.Button(self.root, text="Add Banned Site",
                                         width=20, height=2,
                                         font=("Arial", 12),
                                         command=self.add_banned_site)
        self.add_site_button.pack()

        self.remove_site_button = tk.Button(self.root,
                                            text="Remove Banned Site",
                                            width=20, height=2,
                                            font=("Arial", 12),
                                            command=self.remove_banned_site)
        self.remove_site_button.pack()

    def view_banned_sites(self):
        # Function to handle viewing banned sites
        banned_sites = self.send_request(
            {'action': 'get_banned_sites', 'username': self.username})
        if banned_sites is None:
            messagebox.showerror("Error", "Failed to retrieve banned sites.")
        else:
            self.display_banned_sites(banned_sites)

    def display_banned_sites(self, banned_sites):
        # Function to display the list of banned sites in a new window
        banned_sites_window = tk.Toplevel(self.root)
        banned_sites_window.title("Banned Sites")

        # Create a label to show the title
        title_label = tk.Label(banned_sites_window,
                               text="List of Banned Sites",
                               font=("Arial", 14, "bold"))
        title_label.pack()

        # Create a listbox to display the banned sites
        listbox = tk.Listbox(banned_sites_window, width=50, height=10)
        for site in banned_sites:
            listbox.insert(tk.END, site)
        listbox.pack(padx=10, pady=10)

        # Add a close button to close the window
        close_button = tk.Button(banned_sites_window, text="Close",
                                 command=banned_sites_window.destroy)
        close_button.pack(pady=5)

        # Center the window on the screen
        banned_sites_window.geometry("+%d+%d" % (
            self.root.winfo_screenwidth() / 2 - banned_sites_window.winfo_reqwidth() / 2,
            self.root.winfo_screenheight() / 2 - banned_sites_window.winfo_reqheight() / 2))

        # Make the window modal
        banned_sites_window.transient(self.root)
        banned_sites_window.grab_set()

        # Wait for the window to be closed
        self.root.wait_window(banned_sites_window)

    def add_banned_site(self):
        site = simpledialog.askstring("Add Banned Site",
                                      "Enter the site you want to ban:")
        if site:
            self.send_request({'action': 'add_banned_site',
                               'username': self.username,
                               'site': site})

    def remove_banned_site(self):
        site = simpledialog.askstring("Remove Banned Site",
                                      "Enter the site you want to remove "
                                      "from the ban list:")
        if site:
            self.send_request({'action': 'remove_banned_site',
                               'username': self.username,
                               'site': site})

    def send_request(self, data):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(self.server_address)
                serialized_data = pickle.dumps(data)
                # s.sendall(serialized_data)
                Protocol.send_bin(s, serialized_data)

                # Receive the response from bigServer
                response_data = Protocol.recv(s)
                # response_data = s.recv(CHUNK_SIZE_L)
                return pickle.loads(response_data)
        except Exception as e:
            return None  # Ensure None is returned on error.


def is_admin():
    try:
        # Checks if the script is running as admin on Windows
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False  # Not running on Windows or other error


if __name__ == '__main__':
    if not is_admin():
        print("Not running as admin, elevating...")
        elevate()  # Elevate the code to administrative level
    else:
        print("Running as admin, continuing...")
        # Create and run the GUI application
        root = tk.Tk()
        app = LoginSignUpGUI(root)
        root.mainloop()
