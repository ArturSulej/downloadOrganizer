import os
import filetype
import logging
from os import scandir, rename
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from os.path import splitext, exists, join
from shutil import move

source_dir = r"C:\Users\Artur\Downloads"
dest_dir_image = r"C:\Users\Artur\Downloads\Images"
dest_dir_video = r"C:\Users\Artur\Downloads\Videos"
dest_dir_audio = r"C:\Users\Artur\Downloads\Audio"
dest_dir_archive = r"C:\Users\Artur\Downloads\Archives"
dest_dir_document = r"C:\Users\Artur\Downloads\Documents"
dest_dir_font = r"C:\Users\Artur\Downloads\Fonts"
dest_dir_app = r"C:\Users\Artur\Downloads\Application"
dest_dir_pdf = r"C:\Users\Artur\Downloads\PDFs"
dest_dir_exe = r"C:\Users\Artur\Downloads\EXEs"


def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name


def move_file(dest, entry, name):
    if exists(f"{dest}/{name}"):
        unique_name = make_unique(dest, name)
        old_name = join(dest, name)
        new_name = join(dest, unique_name)
        rename(old_name, new_name)
    move(entry, dest)


class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                if os.path.isfile(entry):
                    file_type = filetype.guess(r"{}\{}".format(source_dir, entry.name))
                    name = entry.name
                    dest = source_dir
                    moved = True

                    # Only my computer:
                    if name == "Applications" or name.endswith('.tmp') or name.endswith('.crdownload'):
                        if name != "Applications":
                            logging.info(f'File still being downloaded - {name}')
                        continue

                    if file_type is None:
                        logging.info(f'Cannot guess file type - {name}')
                    else:
                        match file_type.mime.partition("/")[0]:
                            case "image":
                                dest = dest_dir_image
                            case "video":
                                dest = dest_dir_video
                            case "audio":
                                dest = dest_dir_audio
                            case "application":
                                if file_type.extension == "zip" or file_type.extension == "tar" or file_type.extension == "rar" or file_type.extension == "gz" or file_type.extension == "bz2" or file_type.extension == "7z":
                                    dest = dest_dir_archive
                                elif file_type.extension == "epub" or file_type.extension == "doc" or \
                                        file_type.mime.partition("/")[2][0:3] == "vnd":
                                    dest = dest_dir_document
                                elif file_type.mime.partition("/")[2][0:4] == "font":
                                    dest = dest_dir_font
                                elif file_type.extension == "pdf":
                                    dest = dest_dir_pdf
                                elif file_type.extension == "exe":
                                    dest = dest_dir_exe
                                else:
                                    dest = dest_dir_app
                            case _:
                                logging.info(f"Cannot guess file type: {name}")
                                moved = False

                        if moved:
                            move_file(dest, entry, name)
                            logging.info(f"Moved file: {name} to {dest}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
