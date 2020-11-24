from tkinter import *
from tkinter import filedialog, scrolledtext
from PIL import Image, ImageTk
import numpy as np
import os


global path_file_encode
global path_to_image_encode
global path_to_image_decode

padding = 15
preview_image_display_size = 300, 300
file_name_delimiter = "$f1n0"
delimiter = "$t3g0"
save_file_name = True

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

def load_file_to_encode():
    global path_file_encode
    path_file_encode = filedialog.askopenfilename()
    path_file_label = Label(encode_frame, text=path_file_encode, font=("Times New Roman", 16))
    path_file_label.grid(row=4, column=0, sticky=N+E+S+W, padx=padding, pady=padding)
    

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
        message_label = Label(encode_frame, text="ERROR: Tipo de imagen incompatible.", bg='IndianRed1', font=("Times New Roman", 16))
        message_label.grid(row=4, column=0, sticky=N+E+S+W, padx=padding, pady=padding)
        return
    total_pixels = image_matrix.size//bytes_per_pixel
    m_file = open(path_file_encode, "rb")
    data = m_file.read()
    m_file.close()
    # Get data bits
    bits_message = ''.join(format(byte, "08b") for byte in data)
    # Get data delimiter bits
    bits_message += ''.join([format(ord(i), "08b") for i in delimiter])
    if save_file_name:
        # Get file name and extension bits
        bits_message += ''.join([format(ord(i), "08b") for i in os.path.basename(str(m_file.name))])
        # Get file name and extension delimiter bits
        bits_message += ''.join([format(ord(i), "08b") for i in file_name_delimiter])

    required_pixels = len(bits_message)

    if required_pixels > total_pixels:
        error_message = "ERROR: Tamaño insuficiente para el archivo. Debe utilizar una imagen con " \
            + str(required_pixels) + " pixeles o mas. Su imagen tiene " \
                + str(total_pixels) + " pixeles."
        print(error_message)
        message_label = Label(encode_frame, text=error_message, bg='IndianRed1', font=("Times New Roman", 16))
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
        d_message_label = Label(decode_frame, text="ERROR: Tipo de imagen incompatible.", bg='IndianRed1', font=("Times New Roman", 16))
        d_message_label.grid(row=4, column=1, sticky=N+E+S+W, padx=padding, pady=padding)
        return
    
    total_pixels = image_matrix.size//bytes_per_pixel

    hidden_bits = ""
    for pixel in range(total_pixels):
        for q in range(m, bytes_per_pixel):
            hidden_bits += (bin(image_matrix[pixel][q])[2:][-1])
    
    hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]

    message = ""
    filename = ""
    message_found_index = 0

    # Look for message delimiter
    for message_index in range(len(hidden_bits)):
        if message[-5:] == delimiter:
            message_found_index = message_index
            break
        else:
            message += chr(int(hidden_bits[message_index], 2))

    if save_file_name:
        # Look for filename delimiter
        for filename_index in range(len(hidden_bits)):
            if filename[-5:] == file_name_delimiter:
                break
            else:
                filename += chr(int(hidden_bits[filename_index + message_found_index], 2))
    
    if delimiter in message:
        result = message[:-5]
    else:
        result = "No se encontro ningun mensaje secreto"
        d_message_label = Label(decode_frame, text=result, bg='IndianRed1', font=("Times New Roman", 16))
        d_message_label.grid(row=4, column=1, sticky=N+E+S+W, padx=padding, pady=padding)
        print(result)
        return
    if save_file_name:
        if file_name_delimiter in filename:
            filename_result = filename[:-5]
        else:
            filename_result = "No se encontro el nombre del archivo"
            d_message_label = Label(decode_frame, text=result, bg='IndianRed1', font=("Times New Roman", 16))
            d_message_label.grid(row=4, column=1, sticky=N+E+S+W, padx=padding, pady=padding)
            print(filename_result)
            return
    
    print("Imagen decodificada exitosamente.")
    result_directory = os.getcwd() + "/results/"
    if not os.path.exists(os.path.dirname(result_directory)):
        try:
            os.makedirs(os.path.dirname(result_directory))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    print(result_directory)
    if save_file_name:
        file_path = result_directory + filename_result
        print(file_path)
        m_file = open(file_path, "w", encoding='utf8')
    else:
        file_path = result_directory + filename_result
        print(file_path)
        m_file = open(file_path, "w", encoding='utf8')
    m_file.write(result)
    m_file.close()
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

on_click_button = Button(encode_frame, text='Elegir imagen', bg='white', fg='black', command=load_image_encode)
on_click_button.grid(row=1, column=0, sticky=N+E+S+W, padx=padding, pady=padding)
file_on_click_button = Button(encode_frame, text='Elegir archivo', bg='white', fg='black', command=load_file_to_encode)
file_on_click_button.grid(row=3, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

encode_button = Button(encode_frame, text="Confirmar", bg='white', fg='black', command=encode)
encode_button.grid(row=5, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

# ---------------------------------------------------------------------------------------------------------------

# Decrypt --------------------------------------------------------------------------------------------------------

d_title = Label(decode_frame, text='Desencriptar', font=("Times New Roman", 24))
d_title.grid(row=0, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

d_on_click_button = Button(decode_frame, text='Elegir imagen', bg='white', fg='black', command=load_image_decode)
d_on_click_button.grid(row=1, column=0, sticky=N+E+S+W, padx=padding, pady=padding)

d_button = Button(decode_frame, text="Confirmar", bg='white', fg='black', command=decode)
d_button.grid(row=3, column=0, sticky=N+E+S+W, padx=padding, pady=padding)
# ---------------------------------------------------------------------------------------------------------------

encode_frame.pack(side=LEFT)
decode_frame.pack(side=RIGHT)

app.mainloop()

