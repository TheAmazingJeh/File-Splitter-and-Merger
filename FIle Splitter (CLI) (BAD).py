import os, time, json

from tkinter.filedialog import askopenfilename



current_dir = os.path.dirname(os.path.realpath(__file__))

def load_config():
    print("Loading config file")
    # Check if config file exists, if not create one
    if not os.path.exists(os.path.join("config.json")):
        print("Config file not found, creating one")
        with open("config.json", "w") as file:
            json.dump({"seg_size_mb": 22}, file, indent=4)

    # Load config file
    with open("config.json", "r") as file:
        return json.load(file)

def get_parent_file_name(filename):
    try:
        split_path = filename.split(".")
        print(split_path)
        if split_path[-1].startswith("part"):
            return filename.replace(f".{split_path[-1]}", "")
    except:
        pass
    return None

def combine_files(filename):
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

    with open(filename, "wb") as file:
        for part in data:
            file.write(part)

    endTime = time.time()
    print(f"Combined {len(data)} parts in {round(endTime - startTime, 4)} seconds")

def split_files(filename, seg_size_mb=22):
    data = []
    i = 1
    startTime = time.time()
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
    print(f"Split into {i-1} parts in {round(endTime - startTime, 4)} seconds")

if __name__ == "__main__":
    cfg = load_config()
    print(f"Hello, {os.getlogin()}")
    print(f"Select option:\n1. Split file\n2. Combine file")
    while True:
        choice = input(">>>")
        match choice:
            case "1":
                filename = askopenfilename(title="Select any file:", initialdir=current_dir)
                if filename == None or filename == "":
                    print("Invalid file")
                    break

                split_files(filename, cfg["seg_size_mb"])

            case "2":
                filename = askopenfilename(title="Select any part:", initialdir=current_dir)
                filename = get_parent_file_name(filename)
                if filename == None or filename == "":
                    print("Invalid file")
                    break
                combine_files(filename)
            case _:
                print("Invalid choice")
                continue