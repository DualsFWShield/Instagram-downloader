import tkinter as tk
from tkinter import filedialog
import os
import instaloader
import requests
import subprocess

class InstagramMediaDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Media Downloader")
        self.root.geometry("400x200")

        # Create input fields
        self.username_label = tk.Label(root, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(root, width=30)
        self.username_entry.pack()

        self.output_folder_label = tk.Label(root, text="Output Folder:")
        self.output_folder_label.pack()
        self.output_folder_entry = tk.Entry(root, width=30)
        self.output_folder_entry.pack()
        self.browse_button = tk.Button(root, text="Browse", command=self.browse_output_folder)
        self.browse_button.pack()

        # Create download button
        self.download_button = tk.Button(root, text="Download Media", command=self.download_media)
        self.download_button.pack()

        # Create status label
        self.status_label = tk.Label(root, text="")
        self.status_label.pack()

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory()
        self.output_folder_entry.delete(0, tk.END)
        self.output_folder_entry.insert(0, folder_path)

    def download_media(self):
        username = self.username_entry.get()
        output_folder = self.output_folder_entry.get()

        if not username or not output_folder:
            self.status_label.config(text="Please fill in all fields", fg="red")
            return

        try:
            self.install_dependencies()
            self.download_media_internal(username, output_folder)
            self.status_label.config(text="Media downloaded successfully!", fg="green")
        except Exception as e:
            self.status_label.config(text=f"Error: {str(e)}", fg="red")

    def install_dependencies(self):
        dependencies = ["instaloader", "requests"]
        for dependency in dependencies:
            try:
                __import__(dependency)
            except ImportError:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dependency])

    def download_media_internal(self, username, output_folder):
        ig = instaloader.Instaloader()
        profile = instaloader.Profile.from_username(ig.context, username)

        # Create a subfolder with the username
        username_folder = os.path.join(output_folder, username)
        if not os.path.exists(username_folder):
            os.makedirs(username_folder)

        # Save account information to a text file
        account_info_file = os.path.join(username_folder, "account_info.txt")
        with open(account_info_file, "w") as f:
            f.write(f"Username: {username}\n")
            f.write(f"Full Name: {profile.full_name}\n")
            f.write(f"Profile Picture URL: {profile.profile_pic_url}\n")
            f.write(f"Followers: {profile.followers}\n")

        # Download profile picture
        profile_picture_url = profile.profile_pic_url
        profile_picture_file = os.path.join(username_folder, "profile_picture.jpg")
        response = requests.get(profile_picture_url, stream=True)
        with open(profile_picture_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024): 
                if chunk:
                    f.write(chunk)

        # Download media
        for post in profile.get_posts():
            if post.is_video:
                video_url = post.video_url
                file_name = os.path.join(username_folder, f"{post.shortcode}.mp4")
                response = requests.get(video_url, stream=True)
                with open(file_name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024): 
                        if chunk:
                            f.write(chunk)
            else:
                image_url = post.url
                file_name = os.path.join(username_folder, f"{post.shortcode}.jpg")
                response = requests.get(image_url, stream=True)
                with open(file_name, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024): 
                        if chunk:
                            f.write(chunk)

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramMediaDownloader(root)
    root.mainloop()
