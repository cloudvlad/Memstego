import PIL
import requests
import webbrowser
import json
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
    binary_representation = str(binary_representation) + "0000000000000000"
    # Padding the binary sequence with additinal bites for correct pixel encoding
    while len(binary_representation) % 3 != 0:
        binary_representation += "0"
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
        image.show()
        width, height = image.size

        rgb_image = image.convert("RGB")

        for r in range(0, height):
            for c in range(0, width):
                rgb_pixel = rgb_image.getpixel((r, c))
                print(rgb_pixel)
                for i in range(0, 3):
                    byte_sequence += str(rgb_pixel[i] % 2)
        return byte_sequence

    except:
        pass # TODO

def bytes_insertion(image_base, byte_sequence: str) -> None:
    try:
        image = Image.open(image_base)
        # image.show()
        width, height = image.size

        
        rgb_image = image.convert("RGB")
        rgb_image.show()
        byte_cur = 0
        length = len(byte_sequence)
        # print(length)
        for r in range(0, height):
            for c in range(0, width):
                rgb_pixel = rgb_image.getpixel((r, c))
                new_pixel = list(rgb_pixel)
                # print("-")
                # print(rgb_pixel)
                for i in range(0, 3):
                    if byte_cur == length:
                        print("Insertation")
                        print(rgb_image.getpixel((0,0)))
                        print(rgb_image.getpixel((0,1)))
                        print(rgb_image.getpixel((0,2)))
                        print(rgb_image.getpixel((0,3)))
                        image.save(select_directory_to_save())
                        return
                    # print(".")
                    # print(rgb_pixel[i])
                    # print(str(byte_sequence[byte_cur]))
                    if rgb_pixel[i] % 2 != int(byte_sequence[byte_cur]):
                        if rgb_pixel[i] != 0:
                            if byte_sequence[byte_cur] != '0':
                                new_pixel[i] = 0
                                #rgb_pixel[i] = 0 # rgb_pixel[i] + 1
                            else:
                                new_pixel[i] = 0
                                #rgb_pixel[i] = 0 # rgb_pixel[i] - 1
                        else:
                            if byte_sequence[byte_cur] == '1':
                                new_pixel[i] = 0
                                #rgb_pixel[i] = 0 # rgb_pixel[i] + 1
                    else:
                        new_pixel[i] = 0
                        byte_cur += 1
                        #rgb_pixel[i] = 0 # rgb_pixel[i]
                print(new_pixel)
                rgb_image.putpixel((r, c), tuple(new_pixel))
                    
        rgb_image.save(select_directory_to_save())
        print("hello")
        return

    except:
        pass # TODO



def preview_meme():
    webbrowser.open_new(selected_meme_url)

def select_image():
    allowed_filetypes = (
        ("JPG files", "*.jpg"),
        ("PNG files", "*.png")
    )

    filename = fd.askopenfilename(title="Open a file", initialdir="/", filetypes=allowed_filetypes)

    return filename

def select_message():
    allowed_filetypes = (("text files", "*.txt"),)
    filename = fd.askopenfilename(title="Open a file", initialdir="/", filetypes=allowed_filetypes)
    return filename

def select_directory_to_save() -> str:
    filename = fd.asksaveasfile(title="Save file")
    print(filename.name)
    return filename

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
        bytes_insertion(image, binary_represented_message)
        # print("Base64: " + encrypted_message)
        print("Binary: " + binary_represented_message)
        # print("Decrypted from Base64: " + message_decryption(password, encrypted_message))
        # print("Base64 from binary: " + binary_to_string(binary_represented_message))
        # print("UTF-8 from binary: " + message_decryption(password, binary_to_string(binary_represented_message)))

        return
    except:
        pass # TODO

def decrypt(image_url: str, password: str) -> str:
    try:
        binary_represented_message = bytes_extraction(image_url)
        print(binary_represented_message + "||")
        print(binary_to_string(binary_represented_message) + "||")
        message = message_decryption(password, binary_to_string(binary_represented_message))
        print(message + "||")
        return message
    except:
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