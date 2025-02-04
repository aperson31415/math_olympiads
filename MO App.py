# 1.6 MO Files

# Allow drawing over papers, save as {current_paper} overlay{page_number}

# 1.7 : Add data : What has answers? Answer Checking

# 1.8/2.0 : Fix up style, code etc/Release

import tkinter as tk
from tkinter import filedialog
from functools import partial
from PIL import Image, ImageDraw, ImageTk
import pymupdf as fitz # PyMuPDF
import os

# Useless functions (now)

def submit():
    global Qid, answer

# Variable definitions (for global)

lPaper = None
imageon = 0
next_button, prev_button, canvas, current_page, pdf_document = None, None, None, None, None

last_x, last_y = 0, 0
drawinpad = None
mode = "draw"
draw = None
mode_button = None

current_paper = None
page_entry = None

# File Dirs ( Current available MO papers )

def get_files(folder_path='.\\'):
    items = os.listdir(folder_path)
    files = []
    for item in items:
        if os.path.isfile( os.path.join(folder_path, item) ):
            files.append([item, os.path.join(folder_path, item)])
    return files

def get_folders(folder_path='.\\'):
    items = os.listdir(folder_path)
    folders = []
    for item in items:
        if not os.path.isfile( os.path.join(folder_path, item) ):
            folders.append([item, os.path.join(folder_path, item)])
    return folders

def get_normal_folders(folders):
    special_folders = ['books', 'images']
    normals = []
    for i in folders:
        if not(i[0] in special_folders):
            # Is it as solutions folder?
            if not(i[0][-14:] == 'With Solutions'):
                normals.append(i)
    return normals

def get_solution_folders(folders):
    solutions = []
    for i in folders:
        if i[0][-14:] == 'With Solutions':
            solutions.append(i)
    return solutions

def unpack_files(files):
    data = {}
    for [item, path] in files:
        data[path] = item[:item.index('.')]
    return data

# Functions
content = None
def destroycontent():
    global content;
    global current_paper;
    
    if content in [None, '', []]:
        return None
    if type(content) == list:
        for i in content:
            if not i == None:
                i.destroy()
    else:
        content.destroy()

    content = []
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(0, weight=0)


def on_closing(*args, **kwargs):
    root.destroy()

# Basic Tk

root = tk.Tk()
root.title('Maths Olympiad Training')
root.config(bg="white")
root.geometry('1900x850+0+0')

title = tk.Label(text='Maths Olympiad Training', font=('Helvetica', 30, 'bold'), bg='white')
title.grid(row=0, column=0, columnspan=999, sticky='ew')

def page(name):
    global title, next_button, prev_button, canvas, root;
    if next_button:
        next_button.destroy()
        prev_button.destroy()
        canvas.destroy()
        root.grid_rowconfigure(1, weight=0)
    title.destroy()
    title = tk.Label(text=f'Maths Olympiad Training - {name}', font=('Helvetica', 30, 'bold'), bg='white')
    title.grid(row=0, column=0, columnspan=999, sticky='ew')
    return title

# Menu-bar functions

def books():
    global content;
    destroycontent()
    page('books')
    # More later
    files = get_files('books')
    content = []
    things = unpack_files(files)
    j = 0
    for i in things:
        j += 1
        content.append( tk.Button(text=things[i], command=partial(book, i), bg='white', font=('Helvetica', 15)) )
        content[-1].grid(row=j%20, column=int(j//20), sticky='nw')
    return content

def book(filepath):
    page(f'{filepath}')
    destroycontent()
    createPDFframe()
    openPDF(filepath)
    show_page(0)
    return None

def homepage():
    destroycontent()
    page('home')
    # Add padding and fix areas
    global content, root, lPaper;
    subtitle1 = tk.Label(text='Recommended Papers', font=('Helvetica', 20, 'bold'), bg='white')
    subtitle2 = tk.Label(text='Statistics', font=('Helvetica', 20, 'bold'), bg='white')
    subtitle3 = tk.Label(text='Other', font=('Helvetica', 20, 'bold'), bg='white')
    last_paper = tk.Button(text='Last Paper', command = partial(paper, lPaper), bg='white')
    notepad = tk.Button(text='Notepad', command=opennotepad, bg='white')
    nextcomp = tk.Label(text='Next Competition\nCompetition Date Difficulty', bg='white')
    stats = tk.Label(text='Skill:x', bg='white')
    
    content = [subtitle1, subtitle2, subtitle3, last_paper, notepad, nextcomp, stats, content]
    content[0].grid(row=1, column=0, sticky='nw')
    content[1].grid(row=1, column=1, sticky='nw')
    content[2].grid(row=1, column=2, sticky='nw')
    content[3].grid(row=2, column=0, sticky='nw')
    content[4].grid(row=2, column=2, sticky='nw')
    content[5].grid(row=3, column=2, sticky='nw')
    content[6].grid(row=2, column=1, sticky='nw')

def add_select(Menu, label, command):
    Menu.add_command(label=label, command=command)
    return Menu

def papers(competition):
    page(f'{competition} papers')
    global content
    destroycontent()
    
    files = get_files(competition)
    content = []
    things = unpack_files(files)
    j = 0
    for i in things:
        content.append( tk.Button(text=things[i], command=partial(paper, i), bg='white', font=('Helvetica', 15)) )
        content[-1].grid(row=(j%20)+1, column=int(j//20), sticky='nw')
        j += 1


def info(topic):
    global content
    destroycontent()
    # Load content
    if topic == 'competition details':
        content = tk.Label(text='Comp Name:\nDate\nDifficulty\nOther', bg='white', font=('Helvetica', 15))
    elif topic == 'your statistics':
        content = tk.Label(text='Skill: 0\nCurrent Difficulty: ...', bg='white', font=('Helvetica', 15))
    content.grid(row=1, column=0, columnspan=999)
    page(topic)
    return content

# Pages
def paper(file):
    global content, question, qselect, root, qid, Qid, answer
    global current_paper
    page(file)
    destroycontent()
    content = []

    # Question No. Select
    qid = tk.StringVar(master=root)
    qid.set('Question 1')
    Qid = qid.get()
    content.append( tk.OptionMenu(root, qid, 'Question 1', 'Question 2', 'Question 3') )
    content[0].grid(row=3, column=0, sticky='nw')

    # Answer textbox
    content.append( tk.Entry(master=root, font=('Helvetica', 15)) )
    content[1].grid(row=3, column=1, sticky='nw')
    answer = content[1].get()

    # Button
    content.append( tk.Button(text='Submit', command=submit) )
    content[2].grid(row=3, column=2, sticky='nw')
    
    createPDFframe()
    openPDF(file)

    stripfile = file[:file.index('.')]
    while '\\' in stripfile:
        stripfile = stripfile[stripfile.index('\\')+1:]

    current_paper = stripfile

    # Have you been here before?
    if not os.path.exists(f'images\\{current_paper} 0.png'):
        blank_paper = Image.new("RGB", (800, 600), "white")
        blank_paper.save(f".\\images\\{current_paper} 0.png")

    opennotepad('nextto')
    return content

# PDF Papers

def openPDF(filename):
    global current_page, pdf_document;
    current_page = 0
    pdf_document = fitz.open(filename)
    show_page(0)

def show_page(page_number):
    global canvas, current_page, pdf_document, page_entry

    if page_number == None:
        page_number = page_entry.get()
    
    if page_number in ['', []]:
        return False

    try:
        page_number = int(page_number)
    except Exception:
        page_number = current_page
    
    if int(page_number) >= len(pdf_document) - 1:
        Page_number = len(pdf_document) - 1
    elif int(page_number) <=0:
        Page_number = 0
    else:
        Page_number = int(page_number)
    
    page = pdf_document.load_page(Page_number)
    pix = page.get_pixmap()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    img_resized = img.resize( ( int( img.width // 1.2 ), int( img.height // 1.2 ) ) ) # Change width and height here
    tk_img = ImageTk.PhotoImage(img_resized)
    
    canvas.delete('all')
    canvas.create_image(0, 0, anchor='nw', image=tk_img)
    canvas.image = tk_img
    current_page = Page_number

def next_page():
    global pdf_document, current_page
    if current_page < len(pdf_document) - 1:
        show_page(current_page + 1)

def prev_page():
    global pdf_document, current_page
    if current_page > 0:
        show_page(current_page - 1)

def createPDFframe():
    destroycontent()
    global canvas, current_page, root, page_entry, page_to_go;
    global content;
    
    next_button = tk.Button(text='Next Page', command=next_page, font=('Helvetica', 10), bg='white')
    prev_button = tk.Button(text='Previous Page', command=prev_page, font=('Helvetica', 10), bg='white')
    canvas = tk.Canvas(bg='white')
    
    page_entry = tk.Entry(master=root, font=('Helvetica', 15))
    page_to_go = page_entry.get()
    enter_button = tk.Button(text='Go to page', command = partial( show_page , None ) , bg='white')

    content += [next_button, prev_button, canvas, page_entry, enter_button]
    content[-5].grid(row=2, column=1, sticky='nw')
    content[-4].grid(row=2, column=0, sticky='nw')
    content[-3].grid(row=1, column=0, sticky='ewns', columnspan=3)
    content[-2].grid(row=3, column=0, sticky='nw')
    content[-1].grid(row=3, column=1, sticky='nw')

    root.grid_rowconfigure(1, weight=1001)
    root.grid_columnconfigure(0, weight=1)
    
    current_page = 0

    return root

# Drawing

def start_action(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

def action(event):
    global last_x, last_y, drawingpad, mode, draw
    if mode == "draw":
        drawingpad.create_line(last_x, last_y, event.x, event.y, width=2, fill="black", capstyle=tk.ROUND, smooth=tk.TRUE)
        # To add to image
        draw.line([last_x, last_y, event.x, event.y], fill="black", width=2)
    elif mode == "erase":
        drawingpad.create_line(last_x, last_y, event.x, event.y, width=20, fill="white", capstyle=tk.ROUND, smooth=tk.TRUE)
        draw.line([last_x, last_y, event.x, event.y], fill="white", width=20)

    last_x, last_y = event.x, event.y

def toggle_mode():
    global mode, mode_button;
    if mode == "draw":
        mode = "erase"
        mode_button.config(text="Switch to Draw")
    else:
        mode = "draw"
        mode_button.config(text="Switch to Erase")

def save_image(mode="pure"):
    if mode == "pure":
        global image;
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            image.save(file_path)
    elif mode == "nextto":
        global current_paper, imageon
        image.save(f'images\\{current_paper} {imageon}.png')

def load_image():
    # Always pure mode
    global drawingpad
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if file_path:
        global image, draw, img_tk
        image = Image.open(file_path)
        draw = ImageDraw.Draw(image)
        
        img_tk = ImageTk.PhotoImage(image)
        drawingpad.create_image(0, 0, anchor=tk.NW, image=img_tk)

def path_image(path_file):
    # Always nextto mode
    global drawingpad
    global image, draw, img_tk
    image = Image.open(path_file)
    draw = ImageDraw.Draw(image)
        
    img_tk = ImageTk.PhotoImage(image)
    drawingpad.create_image(0, 0, anchor=tk.NW, image=img_tk)

def next_image():
    # Always nextto mode
    global imageon, current_paper;
    imageon += 1
    if not os.path.exists(f'images\\{current_paper} {imageon}.png'):
        blank_paper = Image.new("RGB", (800, 600), "white")
        blank_paper.save(f"images\\{current_paper} {imageon}.png")
    
    path_image(f'images\\{current_paper} {imageon}.png')

def prev_image():
    # Always nextto mode
    global imageon, current_paper;
    if imageon > 0:
        imageon -= 1
        path_image(f'images\\{current_paper} {imageon}.png')

def opennotepad(mode='pure'):
    global drawingpad, image, draw;
    global mode_button, save_button, load_button;
    global content, current_paper;
    # pure : notepad by itself, nextto : next to paper
    if mode == 'pure':
        current_paper = 'notepad\\'
        page('notepad')
        
        destroycontent()
        
        drawingpad = tk.Canvas(root, width=800, height=600, bg="white")
    
        last_x, last_y = None, None
        mode = "draw"

        mode_button = tk.Button(root, text="Switch to Erase", command=toggle_mode, bg='white')
        save_button = tk.Button(root, text="Save Drawing", command=partial(save_image, 'nextto'), bg='white')
        saveas_button = tk.Button(root, text="Save Drawing As ...", command=partial(save_image, 'pure'), bg='white')
        load_button = tk.Button(root, text="Load Drawing", command=load_image, bg='white')

        content = [drawingpad, mode_button, save_button, load_button, saveas_button]
        content[0].grid(row=1, column=0, columnspan=999, sticky='nw')
        content[1].grid(row=2, column=0, columnspan=999, sticky='nw')
        content[2].grid(row=3, column=0, sticky='nw')
        content[3].grid(row=3, column=2, sticky='nw')
        content[4].grid(row=3, column=1, sticky='nw')

        image = Image.new("RGB", (800, 600), "white")
        draw = ImageDraw.Draw(image)

        drawingpad.bind("<Button-1>", start_action)
        drawingpad.bind("<B1-Motion>", action)
    elif mode == 'nextto':
        global imageon
        drawingpad = tk.Canvas(root, width=800, height=600, bg="white")
    
        last_x, last_y = None, None
        mode = "draw"

        mode_button = tk.Button(root, text="Switch to Erase", command=toggle_mode, bg='white')
        save_button = tk.Button(root, text="Save Drawing", command=partial(save_image, 'nextto'), bg='white')
        nextdraw_button = tk.Button(root, text="Next Drawing", command=next_image, bg='white')
        prevdraw_button = tk.Button(root, text="Previous Drawing", command=prev_image, bg='white')

        if content != []:
            content += [drawingpad, mode_button, save_button, nextdraw_button, prevdraw_button]
        else:
            for i in [drawingpad, mode_button, save_button, nextdraw_button, prevdraw_button]:
                content.append(i)
        content[-5].grid(row=1, column=4, columnspan=999, sticky='nw')
        content[-4].grid(row=2, column=4, columnspan=999, sticky='nw')
        content[-3].grid(row=3, column=4, sticky='nw')
        content[-2].grid(row=4, column=5, sticky='nw')
        content[-1].grid(row=4, column=4, sticky='nw')

        image = Image.new("RGB", (800, 600), "white")
        draw = ImageDraw.Draw(image)

        drawingpad.bind("<Button-1>", start_action)
        drawingpad.bind("<B1-Motion>", action)

        path_image(f'images\\{current_paper} 0.png')

        imageon = 0
    return drawingpad

# Menu Bar

menu = tk.Menu(root)

papers_menu = tk.Menu(menu, tearoff=0)
normal_folders = get_normal_folders( get_folders('.\\') )
for i in normal_folders:
    add_select(papers_menu, i[0], partial(papers, i[0]))
menu.add_cascade(label="Papers", menu=papers_menu)

solutions_menu = tk.Menu(menu, tearoff=0)
solution_folders = get_solution_folders( get_folders('.\\') )
for i in solution_folders:
    add_select(solutions_menu, i[0], partial(papers, i[0]))
menu.add_cascade(label="Solutions", menu=solutions_menu)

info_menu = tk.Menu(menu, tearoff=0)
add_select(info_menu, "Competition Details", partial(info, 'competition details'))
add_select(info_menu, "Your Statistics", partial(info, 'your statistics'))
menu.add_cascade(label="Information", menu=info_menu)

resources_menu = tk.Menu(tearoff=0)
add_select(resources_menu, "Books", books)
add_select(resources_menu, "Notepad", opennotepad)
menu.add_cascade(label="Resources", menu=resources_menu)

root.config(menu=menu)

if not __name__ == '__main__':
    root.destroy()
else:
    root.protocol("WM_DELETE_WINDOW", on_closing)
    homepage()
