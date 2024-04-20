import os, time, json

from tkinter import Tk, Button, Label, LabelFrame, Frame, Spinbox, Entry
from tkinter import IntVar
from tkinter.messagebox import askyesno, showerror, showinfo
from tkinter.filedialog import askopenfilename
from tkinter.dialog import Dialog


current_dir = os.path.dirname(os.path.realpath(__file__))

def set_entry_text(entry, text):
    entry.config(state="normal")
    entry.delete(0, "end")
    entry.insert(0, text)
    entry.config(state="disabled")

class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master, width=30)

        self.default_placeholder = str(placeholder)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def set_placeholder(self, placeholder):
        self.placeholder = placeholder
        self.put_placeholder()

    def put_placeholder(self):
        self.delete('0', 'end')
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

class App(Tk):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.title("File Splitter")
        self.geometry("455x190")
        self.cfg = self.load_config()
        self.create_split_widgets()
        self.create_merge_widgets()

        self.reload_config()
        self.reload_entries()

    def create_split_widgets(self):
        self.splitFrame = LabelFrame(self, text="Split File")


        self.splitButtonFrame = Frame(self.splitFrame)
        self.splitButton = Button(self.splitButtonFrame, text="Select File", command=self.load_split_file)
        self.splitButton.grid(column=0, row=0, padx=10)
        self.splitStartButton = Button(self.splitButtonFrame, text="Start Split", command=self.split_file_checker)
        self.splitStartButton.grid(column=1, row=0, padx=10)
        self.splitButtonFrame.grid(column=0, row=0, padx=10, pady=10)

        self.splitFileName = Entry(self.splitFrame, width=30, state="disabled")
        self.splitFileName.grid(column=0, row=1, padx=10, pady=10)
        set_entry_text(self.splitFileName, "No file selected")


        self.splitSizeFrame = Frame(self.splitFrame)
        self.splitSizeLabel = Label(self.splitSizeFrame, text="Part Size (MB):")
        self.splitSizeLabel.grid(column=0, row=0)
        self.splitSizeVar = IntVar(value=self.cfg["seg_size_mb"])
        self.splitSizeSpinbox = Spinbox(self.splitSizeFrame, from_=1, to=999, width=5, textvariable=self.splitSizeVar, command=self.reload_config)
        self.bind("<Return>", lambda e: self.reload_config())
        self.splitSizeSpinbox.grid(column=1, row=0)
        self.splitSizeFrame.grid(column=0, row=2, padx=10)

        self.splitStatus = Label(self.splitFrame)
        self.splitStatus.config(text="Status: Idle")
        self.splitStatus.grid(column=0, row=3, padx=10, pady=10)

        self.splitFrame.grid(column=0, row=0, padx=10, pady=10)

    def create_merge_widgets(self):
        self.mergeFrame = LabelFrame(self, text="Merge File")


        self.mergeButtonFrame = Frame(self.mergeFrame)
        self.mergeButton = Button(self.mergeButtonFrame, text="Select File", command=self.load_merge_file)
        self.mergeButton.grid(column=0, row=0, padx=10)
        self.mergeStartButton = Button(self.mergeButtonFrame, text="Start Merge", command=self.merge_files_checker)
        self.mergeStartButton.grid(column=1, row=0, padx=10)
        self.mergeButtonFrame.grid(column=0, row=0, padx=10, pady=10)

        self.mergeFileName = Entry(self.mergeFrame, width=30, state="disabled")
        self.mergeFileName.grid(column=0, row=1, padx=10, pady=10)
        set_entry_text(self.mergeFileName, "No file selected")


        self.mergeFileNameS = EntryWithPlaceholder(self.mergeFrame, placeholder="New File Name")
        self.mergeFileNameS.grid(column=0, row=2)

        self.mergeStatus = Label(self.mergeFrame)
        self.mergeStatus.config(text="Status: Idle")
        self.mergeStatus.grid(column=0, row=3, padx=10, pady=10)

        self.mergeFrame.grid(column=1, row=0, padx=10, pady=10)

    def load_config(self):
        # Check if config file exists, if not create one
        if not os.path.exists(os.path.join("config.json")):
            with open("config.json", "w") as file:
                json.dump({"seg_size_mb": 22}, file, indent=4)

        # Load config file
        with open("config.json", "r") as file:
            config = json.load(file)
        if "loaded_split_file" not in config:
            config["loaded_split_file"] = None
        if "loaded_merge_file" not in config:
            config["loaded_merge_file"] = None

        return config

    def reload_config(self):
        # Save config file
        try:
            self.cfg["seg_size_mb"] = int(self.splitSizeVar.get())
        except:
            self.splitSizeVar.set(22)
            self.reload_config()
            return
        with open("config.json", "w") as file:
            json.dump(self.cfg, file, indent=4)
        # Reload config file
        self.cfg = self.load_config()

    def reload_entries(self):
        f"...{['loaded_split_file'][-27:]}"
        set_entry_text(self.splitFileName, f"...{self.cfg['loaded_split_file'][-27:]}" if self.cfg["loaded_split_file"] != None else "No file selected")
        set_entry_text(self.mergeFileName, f"...{self.cfg['loaded_merge_file'][-27:]}" if self.cfg["loaded_merge_file"] != None else "No file selected")

    def get_parent_file_name(self, filename):
        try:
            split_path = filename.split(".")
            if split_path[-1].startswith("part"):
                return filename.replace(f".{split_path[-1]}", "")
        except:
            pass
        return None

    def split_files(self, filename, seg_size_mb=22):
        data = []
        i = 1

        startTime = time.time()
        # Open file and read in parts
        with open(filename, "rb") as file:
            while True:
                res = file.read(seg_size_mb*10_485_76)
                print(f"Reading part {i}       ", end="\r")
                if res is None or res == b'':
                    break
                i += 1
                data.append(res)

        print(f"Read {i-1} parts             ")

        for j in range(0, len(data)):
            with open(f"{filename}.part{j+1}", "wb") as file:
                file.write(data[j])

        endTime = time.time()
        return f"Split into {i-1} parts in {round(endTime - startTime, 4)} seconds"

    def split_file_checker(self):
        # Check if any file is loaded
        if not os.path.exists(self.cfg["loaded_split_file"]):
            showerror("Error", "No file selected")
            return
        # Check file size
        if os.path.getsize(self.cfg["loaded_split_file"]) < self.cfg["seg_size_mb"]*1_048_576:
            res = askyesno("Warning", "File size smaller than selected part size, split anyway?")
            if res != True:
                return
        
        self.splitStatus.config(text="Status: Running...")
        self.update_idletasks()
        resText = self.split_files(self.cfg["loaded_split_file"], self.cfg["seg_size_mb"])
        self.splitStatus.config(text="Status: Complete!")
        showinfo("Split Complete", resText)
        self.splitStatus.config(text="Status: Idle")
        
    def load_split_file(self):
        filename = askopenfilename(title="Select any file:", initialdir=current_dir)
        self.cfg["loaded_split_file"] = filename
        self.reload_config()
        self.reload_entries()

    def merge_files(self, filename, res_filename):
        print(f"Merging {filename}")
        data = []
        i = 1
        startTime = time.time()
        while True:
            if not os.path.exists(f"{filename}.part{i}"):
                break
            with open(f"{filename}.part{i}", "rb") as file:
                data.append(file.read())
            i += 1

        print(f"File is {len(data)} parts long")
        
        res_filename = os.path.join(os.path.dirname(filename), res_filename)
        with open(res_filename, "wb") as file:
            for part in data:
                file.write(part)

        endTime = time.time()
        print(f"Merged {len(data)} parts in {round(endTime - startTime, 4)} seconds")

    def merge_files_checker(self):
        if self.mergeFileNameS.get() == "":
            showerror("Error", "No file name selected")
            return

        self.mergeStatus.config(text="Status: Running...")
        self.update_idletasks()
        self.merge_files(self.cfg["loaded_merge_file"], self.mergeFileNameS.get())
        self.mergeStatus.config(text="Status: Complete!")
        showinfo("Merge Complete", "Merge Complete!")
        self.mergeStatus.config(text="Status: Idle")

    def load_merge_file(self):
        filename = askopenfilename(title="Select any part:", initialdir=current_dir)
        filename = self.get_parent_file_name(filename)
        print(filename)
        if filename == None or filename == "":
            print("Invalid file")
            return
        self.cfg["loaded_merge_file"] = filename
        # Check if filename is a valid file
        if len(filename) > 5:
            self.mergeFileNameS.set_placeholder(os.path.basename(filename))
        self.reload_config()
        self.reload_entries()


if __name__ == "__main__":
    app = App()
    app.mainloop()
