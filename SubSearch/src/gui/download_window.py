import os
import sys
import tkinter as tk

from src.gui.root import Tks, main
from src.scraper.subscene_soup import get_download_url
from src.utilities.file_manager import clean_up, download_zip_auto, extract_zips
from src.utilities.local_paths import cwd


# download said subtitle to the folder with the video file in it
class DownloadList(tk.Frame):
    def __init__(self, parent) -> None:
        tk.Frame.__init__(self, parent)
        # listbox for the subtitles
        list_box = tk.Listbox(
            root,
            bg=Tks.bg,
            fg=Tks.fg,
            font=Tks.font8b,
            bd=0,
            border=0,
            borderwidth=0,
            highlightthickness=0,
        )
        list_box.place(
            height=Tks.window_height - 60,
            width=Tks.window_width - 20,
            relx=0.5,
            rely=0.525,
            bordermode="inside",
            anchor="center",
        )

        dicts_names = {}
        dicts_urls = {}
        count = 0
        # fil list box with all available subtitles that were found and not downloaded
        for x, i in zip(range(0, len(sublist)), sublist):
            x = i.split(" ")
            match = f"{x[0]} {x[1]}"
            name = x[2]
            url = x[-1]
            txt = f"{match} {name}"
            list_box.insert(tk.END, f"{match} {name}\n")
            list_box.bind("<<ListboxSelect>>", self.download_button)
            dicts_names[count] = txt
            dicts_urls[count] = url
            self.dicts_urls = dicts_urls
            self.dicts_names = dicts_names
            self.list_box = list_box
            count += 1

        # custom scrollbar
        scrollbar_lengt = 50
        self.scrollbar_lengt = scrollbar_lengt
        self.scrollbar_lenght_half = round(scrollbar_lengt / 2)
        scrollbar_canvas = tk.Canvas(root, width=24, height=633)
        scrollbar_canvas.configure(bg=Tks.bc, bd=0, highlightthickness=0)
        self.scrollbar_canvas = scrollbar_canvas
        self.scrollbar = scrollbar_canvas.create_rectangle(
            2, 2, scrollbar_lengt, scrollbar_lengt, fill=Tks.fg, outline=Tks.fg
        )
        scrollbar_canvas.place(x=Tks.window_width - 35, y=51, bordermode="inside")
        # scrollbar binds
        scrollbar_canvas.bind("<ButtonPress-1>", self.scrollbar)  # scrollbar click
        scrollbar_canvas.bind("<ButtonRelease-1>", self.scroll_release)  # scrollbar release
        # custom mousewheel binds
        scrollbar_canvas.tag_bind(id, "<<MouseWheel>>", self.custom_scroll)
        root.bind("<MouseWheel>", self.custom_scroll)

        self.extent = 0

    def custom_scroll(self, event):
        event.widget.event_generate("<<MouseWheel>>")

        # maintain ratio between scrollbar pos and scrollbar canvas length
        old_value = self.extent
        old_min = 0
        old_max = 633
        new_min = 0
        new_max = len(sublist)
        old_range = old_max - old_min
        new_range = new_max - new_min
        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

        # move scrollbar with scrollwheel and prevent scrollbar from going out of bounds
        if new_value <= 0:
            pass
        else:
            if event.delta > 0:
                self.extent -= 25
        if new_value >= 100:
            pass
        else:
            if event.delta < 0:
                self.extent += 25

        # update scrollbar position
        if round(new_value) <= new_max and round(new_value) >= new_min:
            self.scrollbar_canvas.coords(
                self.scrollbar,
                2,
                old_value - self.scrollbar_lenght_half,
                self.scrollbar_lenght_half,
                old_value + self.scrollbar_lenght_half,
            )
        # dirty fix for scrollbar moving further than intended
        if self.list_box.get(round(new_value)) == self.list_box.get(0):
            self.scrollbar_canvas.coords(
                self.scrollbar, 2, self.scrollbar_lengt, self.scrollbar_lenght_half, new_min
            )
        if self.list_box.get(round(new_value)) == self.list_box.get(new_max):
            self.scrollbar_canvas.coords(
                self.scrollbar, 2, old_max, self.scrollbar_lenght_half, 633 - 50
            )
        self.list_box.see(round(new_value))

    def no_op(self, event):
        return "break"

    def scrollbar(self, event):
        # maintain ratio between scrollbar pos and mouse movement in the Y axis
        old_value = event.y
        old_min = 0
        old_max = 633
        new_min = 0
        new_max = len(sublist)
        old_range = old_max - old_min
        new_range = new_max - new_min
        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

        # mouse movement bind while scrollbar is pressed
        self.scrollbar_canvas.bind("<Motion>", self.scrollbar)
        self.extent = old_value

        # prevent scrollbar from going out of bounds
        if new_value <= new_max and new_value >= new_min:
            # move scrollbar with mouse movement Y axis pos
            self.scrollbar_canvas.coords(
                self.scrollbar,
                2,
                old_value - self.scrollbar_lenght_half,
                self.scrollbar_lenght_half,
                old_value + self.scrollbar_lenght_half,
            )
            self.list_box.see(round(new_value))

    def scroll_release(self, event):
        self.scrollbar_canvas.unbind("<Motion>")

    def download_button(self, event) -> None:
        a = str(self.list_box.curselection())
        a = a.replace("(", "")
        a = a.replace(")", "")
        a = a.replace(",", "")
        _error = False
        for (number, url), (name) in zip(self.dicts_urls.items(), self.dicts_names.values()):
            if number == int(a):
                self.list_box.delete(int(number))
                self.list_box.insert(int(number), f"»»» DOWNLOADING «««")
                self.list_box.itemconfig(int(number), {"fg": Tks.dling})
                try:
                    dl_url = get_download_url(url)
                    _name = name.replace("/", "").replace("\\", "").split(": ")
                    path = f"{cwd()}\\{_name[-1]}.zip"
                    item = path, dl_url, 1, 1
                    download_zip_auto(item)
                    if _error is False:
                        extract_zips(cwd(), ".zip")
                        clean_up(cwd(), ".zip")
                        clean_up(cwd(), ").nfo")
                        self.list_box.delete(int(number))
                        self.list_box.insert(int(number), f"✔ {name}")
                        self.list_box.itemconfig(int(number), {"fg": Tks.dled})
                        _error = False
                except OSError:
                    _error = True
                    self.list_box.delete(int(number))
                    self.list_box.insert(int(number), f"⚠⚠⚠ Download failed ⚠⚠⚠")
                    self.list_box.itemconfig(int(number), {"fg": Tks.failed})


# file with subtitles and corresponding dl links
if os.path.exists("temp.txt"):
    with open("temp.txt", "r") as fileopen:
        sublist = [line.strip() for line in fileopen]


root = main()
DownloadList(root).pack(anchor="center")
tk.Frame(root, bg=Tks.bg).pack(anchor="center", expand=True)
root.mainloop()


sys.exit()
