import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import instaloader
from moviepy.editor import VideoFileClip
import os
import threading
import requests


class InstagramDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Video Downloader")

        self.create_widgets()

    def create_widgets(self):
        # URL Entry
        tk.Label(self.root, text="Instagram Post URL:").grid(
            row=0, column=0, padx=10, pady=10)
        self.url_entry = tk.Entry(self.root, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        # Folder Selection
        tk.Label(self.root, text="Download Folder:").grid(
            row=1, column=0, padx=10, pady=10)
        self.folder_entry = tk.Entry(self.root, width=50)
        self.folder_entry.grid(row=1, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Browse...", command=self.browse_folder).grid(
            row=1, column=2, padx=10, pady=10)

        # Audio Option
        self.audio_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="Download as Audio", variable=self.audio_var).grid(
            row=2, column=1, padx=10, pady=10)

        # Download Button
        tk.Button(self.root, text="Download", command=self.start_download).grid(
            row=3, column=1, padx=10, pady=20)

        # Progress Bar
        self.progress = ttk.Progressbar(
            self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=4, column=0, columnspan=3, padx=10, pady=10)
        self.progress['value'] = 0

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def start_download(self):
        url = self.url_entry.get()
        folder = self.folder_entry.get()
        if not url or not folder:
            messagebox.showerror(
                "Error", "Please enter the URL and select a download folder.")
            return

        self.progress['value'] = 0
        self.root.update_idletasks()
        threading.Thread(target=self.download_video,
                         args=(url, folder)).start()

    def update_progress(self, value, max_value):
        percentage = (value / max_value) * 100
        self.progress['value'] = percentage
        self.root.update_idletasks()

    def download_video(self, url, folder):
        try:
            loader = instaloader.Instaloader()
            shortcode = url.split('/')[-2]
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            video_url = post.video_url

            # Download video using requests to show progress
            video_filename = os.path.join(folder, f"{shortcode}.mp4")
            response = requests.get(video_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(video_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        self.update_progress(downloaded_size, total_size)

            if self.audio_var.get():
                # Convert video to audio
                video_clip = VideoFileClip(video_filename)
                audio_filename = video_filename.replace(".mp4", ".mp3")
                video_clip.audio.write_audiofile(audio_filename)
                video_clip.close()
                # Remove the video file after extraction
                os.remove(video_filename)
                messagebox.showinfo(
                    "Success", f"Audio saved as: {audio_filename}")
            else:
                messagebox.showinfo(
                    "Success", f"Video saved as: {video_filename}")

        except Exception as e:
            messagebox.showerror("Error", str(e))

        finally:
            self.progress['value'] = 100
            self.root.update_idletasks()


if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramDownloaderApp(root)
    root.mainloop()
