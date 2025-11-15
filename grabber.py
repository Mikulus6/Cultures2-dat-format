import os
from supplements.library import Library


def generate_all_dat_content(dir_path: str):

    library = Library()
    try:
        library.load(os.path.join(dir_path, "DataX\\Libs\\data0001.lib"), cultures_1=False)
    except FileNotFoundError:
        pass

    for name, data in library.items():
        if name.lower().endswith(".dat"):
            yield data

    try:

        for root, dirs, files in os.walk(dir_path):

            if "map.dat" in files:

                dat_path = os.path.join(root, "map.dat")

                with open(dat_path, "rb") as file:
                    yield file.read()

            for file in files:
                if file.lower().endswith(".c2m"):
                    print(file)
                    c2m_library = Library()
                    c2m_library.load(os.path.join(root, file), cultures_1=False)
                    print(c2m_library.keys())
                    yield c2m_library["currentusermap\\map.dat"]
    except FileNotFoundError:
        pass

# Change this accordingly to your local paths
dirs_dict_ = {"2": "C:\\Users\\Mikolaj\\Games\\Cultures\\Gates of Asgard",
              "3": "C:\\Users\\Mikolaj\\Games\\Cultures\\Wyprawa na Północ",
              "4": "C:\\Users\\Mikolaj\\Games\\Cultures\\8th Wonder",
              "5": "C:\\Users\\Mikolaj\\Games\\Cultures\\Cultures Saga"}


def save_copied_dats(dirs_dict):
    dir_to_copy_to = "grabbed"
    for version, path in dirs_dict.items():
        for num, data in enumerate(generate_all_dat_content(path)):
            os.makedirs(dir_to_copy_to, exist_ok=True)
            with open(os.path.join(dir_to_copy_to, os.path.join(f"{version}_{num}.dat")), "wb") as file:
                file.write(data)

save_copied_dats(dirs_dict_)