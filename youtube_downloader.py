import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pytube import YouTube
from moviepy import AudioFileClip
from threading import Thread

class YouTubeDownloader(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set dark mode colors
        self.bg_color = "#2E2E2E"
        self.fg_color = "#E5E600"
        self.text_color = "#FFFFFF"
        self.entry_bg = "#4A4A4A"
        self.button_bg = "#5A5A5A"
        self.button_fg = "#E5E600"
        self.progress_bg = "#3C3C3C"

        self.title("YouTube Downloader")
        self.geometry("600x400")
        self.configure(bg=self.bg_color)

        self.url_frame = tk.Frame(self, bg=self.bg_color)
        self.url_frame.pack(pady=10)

        self.url_label = tk.Label(self.url_frame, text="YouTube URL:", bg=self.bg_color, fg=self.text_color)
        self.url_label.grid(row=0, column=0, padx=5)

        self.url_entry = tk.Entry(self.url_frame, width=50, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color)
        self.url_entry.grid(row=0, column=1, padx=5)

        self.search_button = tk.Button(self.url_frame, text="Search", command=self.validate_url, bg=self.button_bg, fg=self.button_fg)
        self.search_button.grid(row=0, column=2, padx=5)

        self.dest_label = tk.Label(self, text="Destination Folder:", bg=self.bg_color, fg=self.text_color)
        self.dest_label.pack(pady=10)

        self.dest_entry = tk.Entry(self, width=50, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color)
        self.dest_entry.pack(pady=5)

        self.dest_button = tk.Button(self, text="Browse", command=self.browse_folder, bg=self.button_bg, fg=self.button_fg)
        self.dest_button.pack(pady=5)

        self.format_quality_frame = tk.Frame(self, bg=self.bg_color)
        self.format_quality_frame.pack(pady=10)

        self.format_label = tk.Label(self.format_quality_frame, text="Format:", bg=self.bg_color, fg=self.text_color)
        self.format_label.grid(row=0, column=0, padx=10)

        self.format_var = tk.StringVar(value="mp4")
        self.format_mp4 = tk.Radiobutton(self.format_quality_frame, text="MP4", variable=self.format_var, value="mp4", command=self.update_quality_options, bg=self.bg_color, fg=self.text_color, selectcolor=self.button_bg, state=tk.DISABLED)
        self.format_mp3 = tk.Radiobutton(self.format_quality_frame, text="MP3", variable=self.format_var, value="mp3", command=self.update_quality_options, bg=self.bg_color, fg=self.text_color, selectcolor=self.button_bg, state=tk.DISABLED)
        self.format_mp4.grid(row=0, column=1, padx=5)
        self.format_mp3.grid(row=0, column=2, padx=5)

        self.quality_label = tk.Label(self.format_quality_frame, text="Quality:", bg=self.bg_color, fg=self.text_color)
        self.quality_label.grid(row=0, column=3, padx=10)

        self.quality_var = tk.StringVar()
        self.quality_dropdown = ttk.Combobox(self.format_quality_frame, textvariable=self.quality_var, width=30, state=tk.DISABLED)
        self.quality_dropdown.grid(row=0, column=4, padx=5)
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TCombobox", fieldbackground=self.entry_bg, background=self.entry_bg, foreground=self.text_color)

        self.filename_label = tk.Label(self, text="Filename:", bg=self.bg_color, fg=self.text_color)
        self.filename_label.pack(pady=10)

        self.filename_entry = tk.Entry(self, width=50, bg=self.entry_bg, fg=self.text_color, insertbackground=self.text_color)
        self.filename_entry.pack(pady=5)

        self.download_button = tk.Button(self, text="Download", command=self.start_download, bg=self.button_bg, fg=self.button_fg)
        self.download_button.pack(pady=20)

        self.progress_label = tk.Label(self, text="", bg=self.bg_color, fg=self.text_color)
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5)
        self.style.configure("TProgressbar", troughcolor=self.progress_bg, background=self.fg_color)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder_selected)

    def start_download(self):
        url = self.url_entry.get()
        destination = self.dest_entry.get()
        format = self.format_var.get()
        quality = self.quality_var.get()
        filename = self.filename_entry.get()

        if not url or not destination or not filename:
            messagebox.showerror("Error", "Please enter a valid URL, destination folder, and filename.")
            return

        # Append extension to the filename based on the selected format
        if format == "mp4" and not filename.endswith(".mp4"):
            filename += ".mp4"
        elif format == "mp3" and not filename.endswith(".mp3"):
            filename += ".mp3"

        self.download_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Starting download...")

        thread = Thread(target=self.download_video, args=(url, destination, format, quality, filename))
        thread.start()

    def download_video(self, url, destination, format, quality, filename):
        try:
            yt = YouTube(url, on_progress_callback=self.show_progress)
            if format == "mp4":
                itag = int(quality.split("itag=")[-1])
                stream = yt.streams.get_by_itag(itag)
                stream.download(output_path=destination, filename=filename)
                self.progress_label.config(text="Download complete!")
            else:
                stream = yt.streams.filter(only_audio=True).first()
                if stream:
                    file_path = stream.download(output_path=destination, filename=filename + ".mp4")
                    base, ext = os.path.splitext(file_path)
                    new_file = base + '.mp3'
                    audio_clip = AudioFileClip(file_path)
                    audio_clip.write_audiofile(new_file)
                    audio_clip.close()
                    os.remove(file_path)
                    self.progress_label.config(text="Download complete!")
                else:
                    self.progress_label.config(text="No suitable audio stream found.")
        except Exception as e:
            self.progress_label.config(text="Error: " + str(e))
        finally:
            self.download_button.config(state=tk.NORMAL)

    def validate_url(self):
        url = self.url_entry.get()

        if not url:
            return

        try:
            yt = YouTube(url)
            self.format_mp4.config(state=tk.NORMAL)
            self.format_mp3.config(state=tk.NORMAL)
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, yt.title)
            self.update_quality_options()
        except Exception as e:
            self.format_mp4.config(state=tk.DISABLED)
            self.format_mp3.config(state=tk.DISABLED)
            self.quality_dropdown.config(state=tk.DISABLED)
            messagebox.showerror("Invalid YouTube Link", "The provided YouTube URL is not valid.")

    def update_quality_options(self):
        url = self.url_entry.get()
        format = self.format_var.get()

        if not url:
            return

        try:
            yt = YouTube(url)
            if format == "mp4":
                streams = yt.streams.filter(progressive=True, file_extension="mp4")
            else:
                streams = yt.streams.filter(only_audio=True)

            options = []
            for stream in streams:
                size_mb = stream.filesize / (1024 * 1024)
                option = f"{stream.resolution or 'Audio only'} ({size_mb:.2f} MB) itag={stream.itag}"
                options.append(option)

            self.quality_dropdown["values"] = options
            if options:
                self.quality_dropdown.current(0)
            self.quality_dropdown.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = int((bytes_downloaded / total_size) * 100)
        
        self.progress_bar["value"] = percentage
        self.progress_label.config(text=f"Downloaded: {bytes_downloaded/1024/1024:.2f} MB / {total_size/1024/1024:.2f} MB ({percentage}%)")

if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
