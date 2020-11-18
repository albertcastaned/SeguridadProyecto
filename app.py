from tkinter import *
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk
import numpy as np


global path_to_image_encode
global path_to_image_decode

padding = 15
preview_image_display_size = 300, 300
delimiter = "$t3g0"

def load_image_encode():
    global path_to_image_encode

    path_to_image_encode = filedialog.askopenfilename()

    loaded_image = Image.open(path_to_image_encode)

    loaded_image.thumbnail(preview_image_display_size, Image.ANTIALIAS)

    numpy_loaded_image = np.asarray(loaded_image)
    numpy_loaded_image = Image.fromarray(np.uint8(numpy_loaded_image))
    render = ImageTk.PhotoImage(numpy_loaded_image)
    
    image = Label(encode_frame, image=render)
    image.image = render
    image.grid(row=2, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

def load_image_decode():
    global path_to_image_decode

    path_to_image_decode = filedialog.askopenfilename()

    loaded_image = Image.open(path_to_image_decode)

    loaded_image.thumbnail(preview_image_display_size, Image.ANTIALIAS)

    numpy_loaded_image = np.asarray(loaded_image)
    numpy_loaded_image = Image.fromarray(np.uint8(numpy_loaded_image))
    render = ImageTk.PhotoImage(numpy_loaded_image)
    
    image = Label(decode_frame, image=render)
    image.image = render
    image.grid(row=2, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

def encode():
    global path_to_image_encode
    image = Image.open(path_to_image_encode, 'r')
    width, height = image.size
    image_matrix = np.array(list(image.getdata()))

    if image.mode == 'RGB':
        bytes_per_pixel = 3
        m = 0
    elif image.mode == 'RGBA':
        bytes_per_pixel = 4
        m = 1
    else:
        print("ERROR: Tipo de imagen incompatible.")
        message_label = Label(encode_frame, text="ERROR: Tipo de imagen incompatible.", bg='SpringGreen2', font=("Times New Roman", 16))
        message_label.grid(row=4, column=0, sticky=N+E+S+W, padx=padding, pady=padding)
        return
    
    total_pixels = image_matrix.size//bytes_per_pixel

    secret_message = text.get(1.0, "end-1c")
    secret_message += delimiter

    bits_message = ''.join([format(ord(i), "08b") for i in secret_message])
    required_pixels = len(bits_message)

    if required_pixels > total_pixels:
        print("ERROR: Tamaño insuficiente para el mensaje. Debe utilizar una imagen con mas pixeles, o acortar el mensaje")
        message_label = Label(encode_frame, text="ERROR: Tamaño insuficiente para el mensaje. Debe utilizar una imagen con mas pixeles, o acortar el mensaje", bg='SpringGreen2', font=("Times New Roman", 16))
        message_label.grid(row=4, column=0, sticky=N+E+S+W, padx=padding, pady=padding)
        return
    else:
        index = 0
        for pixel in range(total_pixels):
            for q in range(m, bytes_per_pixel):
                if index < required_pixels:
                    image_matrix[pixel][q] = int(bin(image_matrix[pixel][q])[2:9] + bits_message[index], 2)
                    index += 1
    
    image_matrix = image_matrix.reshape(height, width, bytes_per_pixel)
    encoded_image = Image.fromarray(image_matrix.astype('uint8'), image.mode)
    encoded_image.save(image.filename + "-encrypted.png")
    print("Imagen codificada exitosamente.")

    message_label = Label(encode_frame, text="Imagen codificada exitosamente.", bg='SpringGreen2', font=("Times New Roman", 16))
    message_label.grid(row=4, column=0, sticky=N+E+S+W, padx=padding, pady=padding)


def decode():
    global path_to_image_decode
    image = Image.open(path_to_image_decode, 'r')
    image_matrix = np.array(list(image.getdata()))

    if image.mode == 'RGB':
        bytes_per_pixel = 3
        m = 0
    elif image.mode == 'RGBA':
        bytes_per_pixel = 4
        m = 1
    else:
        d_message_label = Label(decode_frame, text="ERROR: Tipo de imagen incompatible.", bg='SpringGreen2', font=("Times New Roman", 16))
        d_message_label.grid(row=4, column=1, sticky=N+E+S+W, padx=padding, pady=padding)
        return
    
    total_pixels = image_matrix.size//bytes_per_pixel

    hidden_bits = ""
    for pixel in range(total_pixels):
        for q in range(m, bytes_per_pixel):
            hidden_bits += (bin(image_matrix[pixel][q])[2:][-1])
    
    hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]

    message = ""

    for i in range(len(hidden_bits)):
        if message[-5:] == delimiter:
            break
        else:
            message += chr(int(hidden_bits[i], 2))
    if delimiter in message:
        result = message[:-5]
    else:
        result = "No se encontro ningun mensaje secreto"
    d_text.config(state=NORMAL)
    d_text.delete(1.0, END)
    d_text.insert(1.0, result)
    d_text.config(state=DISABLED)

    print(result)
    d_message_label = Label(decode_frame, text="Imagen decodificada exitosamente.", bg='SpringGreen2', font=("Times New Roman", 16))
    d_message_label.grid(row=4, column=1, sticky=N+E+S+W, padx=padding, pady=padding)



app = Tk()
app.state('zoomed')

encode_frame = Frame(app, relief=RAISED, borderwidth=1)
decode_frame = Frame(app, relief=RAISED, borderwidth=1)

app.configure(background='gray60')
app.title("Proyecto de Seguridad")

# Encrypt --------------------------------------------------------------------------------------------------------

title = Label(encode_frame, text='Encriptar', font=("Times New Roman", 24))
title.grid(row=0, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

on_click_button = Button(encode_frame, text='Eligir imagen', bg='white', fg='black', command=load_image_encode)
on_click_button.grid(row=1, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

text = Text(encode_frame, wrap=WORD)
text.grid(row=2, column=1, sticky=E+W, padx=padding, pady=padding)

encode_button = Button(encode_frame, text="Encode", bg='white', fg='black', command=encode)
encode_button.grid(row=3, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

# ---------------------------------------------------------------------------------------------------------------

# Decrypt --------------------------------------------------------------------------------------------------------

d_title = Label(decode_frame, text='Desencriptar', font=("Times New Roman", 24))
d_title.grid(row=0, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

d_on_click_button = Button(decode_frame, text='Eligir imagen', bg='white', fg='black', command=load_image_decode)
d_on_click_button.grid(row=1, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

d_text = Text(decode_frame, wrap=WORD)
d_text.grid(row=2, column=1, sticky=E+W, padx=padding, pady=padding)
d_text.config(state=DISABLED)

d_button = Button(decode_frame, text="Decode", bg='white', fg='black', command=decode)
d_button.grid(row=3, column=0, sticky=N+E+S+W, padx=padding, pady=padding)
# ---------------------------------------------------------------------------------------------------------------

encode_frame.pack(side=LEFT)
decode_frame.pack(side=RIGHT)

app.mainloop()

