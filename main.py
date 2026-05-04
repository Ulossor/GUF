import tkinter as tk
from tkinter import ttk, messagebox
import json
import urllib.request
import threading
import os

root = tk.Tk()
root.title("GitHub User Finder")
root.geometry("600x500")

favorites_data = []
favorites_file = "favorites.json"

search_frame = tk.Frame(root)
search_frame.pack(pady=10, padx=10, fill=tk.X)

tk.Label(search_frame, text="GitHub Username:").pack(side=tk.LEFT)
entry = tk.Entry(search_frame, width=30)
entry.pack(side=tk.LEFT, padx=5)
entry.bind("<Return>", lambda event: do_search())

search_btn = tk.Button(search_frame, text="Search", command=do_search)
search_btn.pack(side=tk.LEFT)

results_frame = tk.Frame(root)
results_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

tk.Label(results_frame, text="Search Results").pack(anchor=tk.W)
tree_results = ttk.Treeview(results_frame, columns=("Login", "Avatar URL"), show="headings", height=8)
tree_results.heading("Login", text="Login")
tree_results.heading("Avatar URL", text="Avatar URL")
tree_results.column("Login", width=150)
tree_results.column("Avatar URL", width=350)
tree_results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll_results = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=tree_results.yview)
scroll_results.pack(side=tk.RIGHT, fill=tk.Y)
tree_results.configure(yscrollcommand=scroll_results.set)

add_fav_btn = tk.Button(root, text="Add to Favorites", command=add_to_favorites)
add_fav_btn.pack(pady=5)

fav_frame = tk.Frame(root)
fav_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

tk.Label(fav_frame, text="Favorites").pack(anchor=tk.W)
tree_favorites = ttk.Treeview(fav_frame, columns=("Login", "Avatar URL"), show="headings", height=6)
tree_favorites.heading("Login", text="Login")
tree_favorites.heading("Avatar URL", text="Avatar URL")
tree_favorites.column("Login", width=150)
tree_favorites.column("Avatar URL", width=350)
tree_favorites.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scroll_fav = ttk.Scrollbar(fav_frame, orient=tk.VERTICAL, command=tree_favorites.yview)
scroll_fav.pack(side=tk.RIGHT, fill=tk.Y)
tree_favorites.configure(yscrollcommand=scroll_fav.set)

remove_fav_btn = tk.Button(root, text="Remove from Favorites", command=remove_from_favorites)
remove_fav_btn.pack(pady=5)

def do_search():
    query = entry.get().strip()
    if not query:
        messagebox.showerror("Error", "Search field cannot be empty")
        return
    threading.Thread(target=search_thread, args=(query,), daemon=True).start()

def search_thread(query):
    url = f"https://api.github.com/search/users?q={query}&per_page=20"
    req = urllib.request.Request(url, headers={"User-Agent": "GitHubUserFinder"})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            items = data.get("items", [])
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Error", str(e)))
        return
    root.after(0, update_results, items)

def update_results(items):
    tree_results.delete(*tree_results.get_children())
    for user in items:
        tree_results.insert("", "end", values=(user["login"], user["avatar_url"]))

def add_to_favorites():
    selection = tree_results.selection()
    if not selection:
        messagebox.showerror("Error", "Select a user from the results")
        return
    item = tree_results.item(selection[0])
    login, avatar = item["values"]
    for fav in favorites_data:
        if fav["login"] == login:
            messagebox.showinfo("Info", "User already in favorites")
            return
    favorites_data.append({"login": login, "avatar_url": avatar})
    tree_favorites.insert("", "end", values=(login, avatar))
    save_favorites()

def remove_from_favorites():
    selection = tree_favorites.selection()
    if not selection:
        messagebox.showerror("Error", "Select a user from favorites")
        return
    item = tree_favorites.item(selection[0])
    login, avatar = item["values"]
    for i, fav in enumerate(favorites_data):
        if fav["login"] == login:
            del favorites_data[i]
            break
    tree_favorites.delete(selection[0])
    save_favorites()

def save_favorites():
    with open(favorites_file, "w") as f:
        json.dump(favorites_data, f, indent=2)

def load_favorites():
    if os.path.exists(favorites_file):
        with open(favorites_file, "r") as f:
            data = json.load(f)
            for fav in data:
                favorites_data.append(fav)
                tree_favorites.insert("", "end", values=(fav["login"], fav["avatar_url"]))

load_favorites()

root.mainloop()
