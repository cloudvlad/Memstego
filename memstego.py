import PIL
import requests
import webbrowser
import json
import math
import tkinter as tk
from tkinter import font
from PIL import ImageTk, Image
from tkinter import ttk, filedialog as fd
from tkinter.messagebox import showinfo
from tkinter.font import BOLD
from io import BytesIO
from random import randrange
import hashlib
import base64
from Crypto.Cipher import AES

BACKGROUND_COLOR = "#FFFFFF"

MODE = AES.MODE_CBC
IV = "5kj14av0cq19q90b"

#logo = ""

selected_meme_url = ""

def main():
    # Main window properties
    main = tk.Tk(className="Mem" + "Stego")
    main.title("MemStego")
    main.geometry("600x500")
    main.resizable(False, False)
    main.configure(background=BACKGROUND_COLOR)
    main.grid_rowconfigure(0, weight=0)
    main.grid_columnconfigure(0, weight=1)
    #icon = ImageTk.PhotoImage(logo)
    #main.iconphoto(False, icon)

    style = ttk.Style()
    style.theme_create("MyStyle", parent="alt", settings={
        "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
        "TNotebook.Tab": {"configure": {"padding": [10, 6],
                                        "font" : ('Arial', '11', 'normal')},}})
    style.theme_use("MyStyle")

    tabControl = ttk.Notebook(main)


    crypt_tab = create_crypt_tab(main)
    decrypt_tab = create_decrypt_tab(main)
    memecrypt_tab = create_memecrypt_tab(main)

    tabControl.add(crypt_tab, text="Crypt")
    tabControl.add(decrypt_tab, text="Decrypt")
    tabControl.add(memecrypt_tab, text="MemeCrypt")

    tabControl.pack(expand=1, fill="both")

    main.mainloop()


# Help functions
def hash_password(password: str) -> str:
    encoded_password = password.encode()
    hashed_password = hashlib.sha256(encoded_password)
    return hashed_password.digest()

def pad_message(message: str) -> str:
    while len(message) % 16 != 0:
        message = message + " "
    return message

def binary_sequenced(message: str) -> str:
    binary_representation = ''.join(format(ord(char), '08b') for char in message)
    binary_representation = str(binary_representation)
    # print(str(binary_representation))
    return binary_representation

def binary_to_string(binary_sequence: str) -> str:
    normalized_message = ""
    cur_point = 0
    length = len(binary_sequence)

    while True:
        # End of bytes
        if cur_point + 8 > length:
            return normalized_message

        # End of message
        if binary_sequence[cur_point:cur_point + 8] == "0000000000000000":
            return normalized_message

        binary_code = binary_sequence[cur_point:cur_point + 8]
        # print(binary_code)
        cur_point = cur_point + 8
        character_code = int(binary_code, 2)
        # print(symbol_code)
        character = chr(character_code)
        normalized_message += character

def strbin_to_int(strbin: str) -> int:
    length = len(strbin)
    number = 0
    power = 0
    for i in range(0, length):
        number = number + (int(strbin[length - i - 1]) * math.pow(2, power))
        power += 1
    return number


def message_encryption(password: str, message: str) -> str:
    key = hash_password(password)
    cipher = AES.new(key, MODE, IV)
    padded_message = pad_message(message)
    encrypted_message = cipher.encrypt(padded_message)
    encoded_message = base64.b64encode(encrypted_message)
    # print(encoded_message.decode())
    return encoded_message.decode()

def message_decryption(password: str, message: str) -> str:
    key = hash_password(password)
    cipher = AES.new(key, MODE, IV)
    decoded_message = base64.b64decode(message)
    decrypted_message = cipher.decrypt(decoded_message)

    return decrypted_message.rstrip().decode()
    
def bytes_extraction(image_url: str) -> str:
    byte_sequence = ""

    try:
        image = Image.open(image_url)
        #image.show()
        width = image.width
        height = image.height

        print("extraction 1")
        rgb_image = image.convert("RGBA")
        rgb_pixel = []
        print("extraction 1.0")
        groups_counter, character_counter, px, py = get_message_info(image_url)
        print("extraction 1.1")
        characters_to_collect = strbin_to_int(character_counter)
        message_info_space = 8 + (strbin_to_int(groups_counter) * 8)
        position = 0
        needed_bits = (characters_to_collect * 8) + message_info_space
        print("extraction 2\n" + characters_to_collect +"\t" + message_info_space + "\t" << needed_bits)
        for x in range(0, width):
            for y in range(0, height):
                rgb_pixel = list(rgb_image.getpixel((x, y)))
                # print(rgb_pixel)
                for i in range(0, 4):
                    if (position > message_info_space and position <= needed_bits):
                        byte_sequence += str(rgb_pixel[i] % 2)
                        print(byte_sequence)

                    if position > message_info_space:
                        return byte_sequence
                    position += 1

        return byte_sequence

    except:
        pass # TODO

def bytes_insertion(image_base, byte_sequence) -> None:
    try:
        image = Image.open(image_base)
        image.show()
        width = image.width
        height = image.height
        print(width, "-", height)
        
        rgb_image = image.convert("RGBA")
        # rgb_image.show()
        byte_cur = 0
        length = len(byte_sequence)
        # print(length)
        for x in range(0, width):
            for y in range(0, height):
                rgb_pixel = rgb_image.getpixel((x, y))
                new_pixel = list(rgb_pixel)
                # print("-")
                # print(new_pixel)
                for i in range(0, 4):
                    if byte_cur == length:
                        rgb_image.show()
                        rgb_image.save(select_directory_to_save())
                        return
                    # print(".")
                    # print(rgb_pixel[i])
                    # print(str(byte_sequence[byte_cur]))
                    if rgb_pixel[i] % 2 != int(byte_sequence[byte_cur]):
                        if rgb_pixel[i] != 0:
                            if byte_sequence[byte_cur] == '1':
                                new_pixel[i] = rgb_pixel[i] + 1
                            else:
                                new_pixel[i] = rgb_pixel[i] - 1
                        else:
                            new_pixel[i] = rgb_pixel[i] + 1
                    else:
                        new_pixel[i] = rgb_pixel[i]
                    byte_cur += 1 

                rgb_image.putpixel((x, y), tuple(new_pixel))
                print(new_pixel)
                    
        rgb_image.show()
        rgb_image.save(select_directory_to_save())
        print("hello")
        return

    except:
        print("upsie")
        pass # TODO


def get_message_info(image_url: str) -> tuple:
    print("get_message_info -1")
    strbin_repres_groups_number = ""
    int_groups_number = 0
    strbin_repres_character_number= ""
    int_character_number = 0

    general_counter = 0

    image = Image.open(image_url)
    image.show()
    width = image.width
    height = image.height

    rgb_image = image.convert("RGBA")
    rgb_pixel = []

    print("get_message_info 0")
    for x in range(0, width):
        for y in range(0, height):
            rgb_pixel = rgb_image.getpixel((x, y))
            new_pixel = list(rgb_pixel)
            print(new_pixel)
            # print(new_pixel):
            if general_counter < 8:
                for i in range(0, 4):
                    print(strbin_repres_groups_number)
                    strbin_repres_groups_number = strbin_repres_groups_number + str(new_pixel[i] % 2)
                    general_counter += 1
                continue

            int_groups_number = strbin_to_int(strbin_repres_groups_number)

            if general_counter < (int_groups_number * 8):
                for i in range(0, 4):
                    print("ch")
                    strbin_repres_character_number = strbin_repres_character_number + str(new_pixel[i] % 2)
                    general_counter += 1
                continue

            break

    print("ending is near")
    return tuple(int_groups_number, int_character_number, x, y)



def put_message_info(encrypted_message: str) -> str:
    message_length = len(encrypted_message)
    groups_counter = ""
    character_counter = ""
    
    length = message_length
    while length >= 1:
        character_counter = str(length % 2) + character_counter
        length = length // 2

    while len(character_counter) % 8 != 0:
        character_counter = "0" + character_counter

    needed_bytes = len(character_counter) / 8
    needed_bytes = math.ceil(needed_bytes)

    while needed_bytes >= 1:
        groups_counter = str(needed_bytes % 2) + groups_counter
        needed_bytes = needed_bytes // 2

    while len(groups_counter) % 8 != 0:
        groups_counter = "0" + groups_counter

    print(groups_counter)
    print(character_counter)
    return groups_counter + character_counter
    

def preview_meme():
    webbrowser.open_new(selected_meme_url)

def select_image():
    allowed_filetypes = (
        ("PNG files", "*.png"),
    )

    filename = fd.askopenfilename(title="Open a file", initialdir="/", filetypes=allowed_filetypes)

    return filename

def select_message():
    allowed_filetypes = (("text files", "*.txt"),)
    filename = fd.askopenfilename(title="Open a file", initialdir="/", filetypes=allowed_filetypes)
    return filename

def select_directory_to_save() -> str:
    filename = fd.asksaveasfile(title="Save file")
    return filename.name

def generate_meme():
    global selected_meme_url
    all_memes = json.loads((requests.get('https://api.memegen.link/images/').content).decode("utf-8"))
    selected_meme_url = (all_memes[randrange(len(all_memes))])['url']
    # print(selected_meme_url)
    if len(selected_meme_url) > 60:
        return selected_meme_url[0:57] + "..."
    return selected_meme_url


# Data operations (Steganography methods)
def image_crypt(image_url: str, message_url: str, password: str) -> None:
    try:
        image = image_url

        message_file = open(message_url, "r")
        message = message_file.read()
        message_file.close()

        encrypted_message = message_encryption(password, message)
        binary_represented_message = binary_sequenced(encrypted_message)
        binary_represented_message = put_message_info(encrypted_message) + binary_represented_message
        bytes_insertion(image, binary_represented_message)

        # print(encrypted_message)
        # print(binary_represented_message)
        # print(message_decryption(password, encrypted_message))
        return

    except:
        pass # TODO

def meme_crypt(message_url: str, password: str) -> None:
    try:
        image = BytesIO((requests.get(selected_meme_url)).content)

        message_file = open(message_url, "r")
        message = message_file.read()
        message_file.close()

        encrypted_message = message_encryption(password, message)
        binary_represented_message = binary_sequenced(encrypted_message)
        binary_represented_message = put_message_info(encrypted_message) + binary_represented_message
        bytes_insertion(image, binary_represented_message)
        # print("Base64: " + encrypted_message)
        # print("Binary: " + binary_represented_message)
        # print("Decrypted from Base64: " + message_decryption(password, encrypted_message))
        # print("Base64 from binary: " + binary_to_string(binary_represented_message))
        # print("UTF-8 from binary: " + message_decryption(password, binary_to_string(binary_represented_message)))

        return
    except:
        pass # TODO

def decrypt(image_url: str, password: str) -> str:
    print("decrypt")
    try:
        binary_represented_message = bytes_extraction(image_url)
        print("decrypt fault 1")
        print(binary_represented_message + "||")
        print("decrypt fault 2")
        print(binary_to_string(binary_represented_message) + "||")
        message = message_decryption(password, binary_to_string(binary_represented_message))
        print(message + "||")
        return message
    except:
        print("decrypt fault")
        pass # TODO





# Tab Creation

def create_crypt_tab(root: tk.Tk):
    frame = ttk.Frame(root)
    image_url_label = ttk.Label(frame, text="*Select image: ", font=("Arial", 12))
    image_url_label.place(x=50, y=50, width=200, height=30)
    image_url = tk.Entry(frame, relief="flat", font=("Arial", 12))
    image_url.place(x=50, y=80, width=400, height=30)
    image_selection = tk.Button(frame, text="...", relief="flat", width=1, height=1, background="#FFFFFF", command=lambda: image_url.insert(0, select_image()))
    image_selection.place(x=450, y=80, width=30, height=30)

    message_url_label = ttk.Label(frame, text="*Select message (.txt): ", font=("Arial", 12))
    message_url_label.place(x=50, y=150, width=200, height=30)
    message_url = tk.Entry(frame, relief="flat", font=("Arial", 12))
    message_url.place(x=50, y=180, width=400, height=30)
    message_selection = tk.Button(frame, text="...", relief="flat", width=1, height=1, background="#FFFFFF", command=lambda: message_url.insert(0, select_message()))
    message_selection.place(x=450, y=180, width=30, height=30)

    password_label = ttk.Label(frame, text="Password: ", font=("Arial", 12))
    password_label.place(x=50, y=250, width=200, height=30)
    password_field = tk.Entry(frame, relief="flat", font=("Arial", 12))
    password_field.place(x=50, y=280, width=430, height=30)

    crypt_button = tk.Button(frame, text="Crypt", command=lambda: image_crypt(image_url.get(), message_url.get(), password_field.get()))
    crypt_button.place(x=50, y=350, width=100, height=35)

    return frame

def create_decrypt_tab(root: tk.Tk):
    frame = ttk.Frame(root)
    image_url_label = ttk.Label(frame, text="*Select image: ", font=("Arial", 12))
    image_url_label.place(x=50, y=50, width=200, height=30)
    image_url = tk.Entry(frame, relief="flat", font=("Arial", 12))
    image_url.place(x=50, y=80, width=400, height=30)
    image_selection = tk.Button(frame, text="...", relief="flat", width=1, height=1, background="#FFFFFF", command=lambda: image_url.insert(0, select_image()))
    image_selection.place(x=450, y=80, width=30, height=30)

    password_label = ttk.Label(frame, text="Password: ", font=("Arial", 12))
    password_label.place(x=50, y=150, width=200, height=30)
    password_field = tk.Entry(frame, relief="flat", font=("Arial", 12))
    password_field.place(x=50, y=180, width=430, height=30)

    crypt_button = tk.Button(frame, text="Decrypt", command=lambda: decrypt(image_url.get(), password_field.get()))
    crypt_button.place(x=50, y=350, width=100, height=35)

    return frame

def create_memecrypt_tab(root: tk.Tk):
    frame = ttk.Frame(root)

    meme_url_label = ttk.Label(frame, text="*Select image: ", font=("Arial", 12))
    meme_url_label.place(x=50, y=50, width=200, height=30)
    meme_url_link = tk.Label(frame, text="\t\t\t\tChoose a random meme -->", relief="flat", font=("Arial", 10, "underline"), cursor="hand2", anchor="w")
    meme_url_link.bind("<Button-1>", lambda e: preview_meme())
    meme_url_link.place(x=50, y=80, width=400, height=30)
    random_meme_button = tk.Button(frame, text="R", relief="flat", width=1, height=1, background="#FFFFFF", command=lambda: meme_url_link.config(text = generate_meme()))
    random_meme_button.place(x=450, y=80, width=30, height=30)

    message_url_label = ttk.Label(frame, text="*Select message (.txt): ", font=("Arial", 12))
    message_url_label.place(x=50, y=150, width=200, height=30)
    message_url = tk.Entry(frame, relief="flat", font=("Arial", 12))
    message_url.place(x=50, y=180, width=400, height=30)
    message_selection = tk.Button(frame, text="...", relief="flat", width=1, height=1, background="#FFFFFF", command=lambda: message_url.insert(0, select_message()))
    message_selection.place(x=450, y=180, width=30, height=30)

    password_label = ttk.Label(frame, text="Password: ", font=("Arial", 12))
    password_label.place(x=50, y=250, width=200, height=30)
    password_field = tk.Entry(frame, relief="flat", font=("Arial", 12))
    password_field.place(x=50, y=280, width=430, height=30)

    crypt_button = tk.Button(frame, text="Crypt", command=lambda: meme_crypt(message_url.get(), password_field.get()))
    crypt_button.place(x=50, y=350, width=100, height=35)

    return frame

if __name__ == "__main__":
    main()