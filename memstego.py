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

# Help functions
def hash_password(password: str) -> str:
    encoded_password = password.encode()
    hashed_password = hashlib.sha256(encoded_password)
    return hashed_password.digest()

def pad_message(message: str) -> str:
        while len(message) % 16 != 0:
            message = message + " "
        return message



def message_encryption(password: str, message: str) -> str:
    key = hash_password(password)
    cipher = AES.new(key, MODE, IV)
    padded_message = pad_message(message)
    encrypted_message = cipher.encrypt(padded_message)
    encoded_message = base64.b64encode(encrypted_message)

    return encoded_message

def message_decryption(password: str, message: str) -> str:
    key = hash_password(password)
    cipher = AES.new(key, MODE, IV)
    decoded_message = base64.b64decode(message)
    decrypted_message = cipher.decrypt(decoded_message)

    return decrypted_message.rstrip().decode()
    

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

def generate_meme():
    global selected_meme_url
    all_memes = json.loads((requests.get('https://api.memegen.link/images/').content).decode("utf-8"))
    selected_meme_url = (all_memes[randrange(len(all_memes))])['url']
    print(selected_meme_url)
    if len(selected_meme_url) > 60:
        return selected_meme_url[0:57] + "..."
    return selected_meme_url


# Data operations (Steganography methods)
def image_data_insert(image_url, message_url, password):
    try:
        image = Image.open(BytesIO((requests.get(selected_meme_url)).content))
        image.show()

        message_file = open(message_url, "r")
        message = message_file.read()
        message_file.close()

        encrypted_message = message_encryption(password, message)
        print(encrypted_message)
        print(message_decryption(password, encrypted_message))
    except:
        pass

    return

def meme_data_insert(message_url: str, password: str) -> None:
    try:
        image = Image.open(BytesIO((requests.get(selected_meme_url)).content))
        image.show()

        message_file = open(message_url, "r")
        message = message_file.read()
        message_file.close()
        encrypted_message = message_encryption(password, message)
        print(encrypted_message)
        print(message_decryption(password, encrypted_message))
    except:
        pass

    return

def data_extract(image_url, aes_key):
    return


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

    aes_key_label = ttk.Label(frame, text="Password: ", font=("Arial", 12))
    aes_key_label.place(x=50, y=250, width=200, height=30)
    aes_key_field = tk.Entry(frame, relief="flat", font=("Arial", 12))
    aes_key_field.place(x=50, y=280, width=430, height=30)

    crypt_button = tk.Button(frame, text="Crypt")
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

    message_url_label = ttk.Label(frame, text="Password: ", font=("Arial", 12))
    message_url_label.place(x=50, y=150, width=200, height=30)
    message_url = tk.Entry(frame, relief="flat", font=("Arial", 12))
    message_url.place(x=50, y=180, width=430, height=30)

    crypt_button = tk.Button(frame, text="Decrypt")
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

    crypt_button = tk.Button(frame, text="Crypt", command=lambda: meme_data_insert(message_url.get(), password_field.get()))
    crypt_button.place(x=50, y=350, width=100, height=35)

    return frame


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


if __name__ == "__main__":
    main()


