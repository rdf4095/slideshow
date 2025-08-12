"""
program: main_0.py

purpose: Main routine for project slideshow.

comments: Demonstrates several different approaches for displaying one or
          more images in succession.

author: Russell Folks

history:
-------
07-02-2025  creation
07-07-2025  Implement 3 methods for display: create image in canvas,
            show with image.show(), plot with matplotlib.
07-09-2025  If image path is string, convert to tuple for opening image file.
            Add enumeration with the canvas option.
07-11-2025  Add Entry for the user to specify pause between images.
07-12-2025  For canvas option, can now resize window before displaying images.
07-14-2025  Add type-hints to funcions. Remove show() method.
08-11-2025  For canvas method, add Entry to display image number and filename.
"""
"""
TODO:
    1. If window is dragged larger, then image is displayed, then reset button is clicked,
       image is not resized. This requires delete() followed by re-display. Need to get
       which image it is...
    2. Debug reset_window_size() to handle a window that has been re-sized
       (currently the total_ht and total_wd don't include the whole ui).
    3. Consider always using the matplotlib method. The main window would
       be reserved for housekeeping (image lists & info, slideshow lists, etc.)
       Main window could also be made minimal, and expand if more info is needed.
"""
import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader
import time

from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt

sttk = SourceFileLoader("styles_ttk", "../styles/styles_ttk.py").load_module()
cnv_ui = SourceFileLoader("cnv", "../canvas/canvas_ui.py").load_module()
sel = SourceFileLoader("ui", "../utilities/tool_classes.py").load_module()

root = ThemedTk()
root.resizable(True, True)
root.title("canvas, ttk, pack")

# canvas = python canvas
# plot   = matplotlib.show
display_method = "canvas"
pause_time = 3

# def reset_window_size(canv: object, dims: str, vp) -> None:
def reset_window_size(canv: object, vp) -> None:
    """Reset the app main window to the global default_dims size."""
    root.geometry(default_dims)

    canv.configure(width=400, height=300)
    vp['w'] = 400
    vp['h'] = 300

    # canv.delete('image')
    canv.configure(width=vp['w'], height=vp['h'])


def open_image_file(canv: object):
    file_path = filedialog.askopenfilenames(title="Select Image File",
                                           initialdir="images",
                                           filetypes=[("Png files", "*.png"),
                                                      ("Jpeg files", "jpg"),
                                                      ("All files", "*.*")]
                                           )
    if file_path:
        add_image(canv, file_path)


def use_canvas(canv: object, fpath: tuple | str):
    """Uses these variables from the module scope:

        pause_time
        textvar
    """
    # if the last image should persist, enable this line:
    global im_tk

    if isinstance(fpath, str):
        fpath = (fpath, )

    for n, item in enumerate(fpath):

        try:
            with Image.open(item) as im:
                imsize = cnv_ui.init_image_size(im, viewport)
                im_resize = im.resize((imsize['w'], imsize['h']))
                im_tk = ImageTk.PhotoImage(im_resize)

                centered_x = (viewport['w'] - imsize['w']) / 2
                centered_y = (viewport['h'] - imsize['h']) / 2
                canv.create_image(centered_x, centered_y, anchor=tk.NW, image=im_tk, tag='image')

                # test
                # print(f'{canv.itemcget('image', 'image')=}')

                fname = item.split('/')[-1]
                lab = str(n+1) + ' of ' + str(len(fpath)) + ': ' + fname
                textvar.set(lab)
                canv.update()
                # ? get size here

            time.sleep(pause_time)
            canv.delete(n)
        except Exception as e:
            print(f'error opening image: {str(e)}')


def use_plot(path: tuple | str):
    """Display a sequence of images using matplotlib.

    Notes:
        1. The isinstance test is only needed if path is passed in as a string.
           There is currently no code to do this.
        2. The figure object is only needed to suppress the window UI widgets
           using pack_forget().
        3. This method does not support the 'with' context manager for reading files.
        4. This method is probably the easier way to have more than one
           independent slideshow (using different figures).
    """
    if isinstance(path, str):
        print('converting path string to tuple...')
        path = (path, )

    # nums = plt.get_fignums()    # list
    # print(f'starting {nums=}')   # empty list, if none

    # with no figure number specified (the 1 in this case), a new
    # figure is automatically created. using an explicit number
    # enables us to return to that figure later.
    # fig = plt.figure(1, figsize=[9.6, 5.0], clear=True)
    fig = plt.figure(figsize=[9.6, 5.0], clear=True)
    # print(f'{fig.number=}')
    nums2 = plt.get_fignums()    # list
    print(f'final {nums2=}')

    for n, item in enumerate(path):
        try:
            im = Image.open(item)
            plt.clf()
            plt.imshow(im)
            plt.axis("off")
            plt.title('image ' + str(n+1))
            fig.canvas.toolbar.pack_forget()
            plt.pause(3)
        except Exception as e:
            print(f'error opening image: {str(e)}')


def add_image(canv: object, fpath: tuple | str):
    global display_method

    match display_method:
        case "canvas":
            use_canvas(canv, fpath)
        case "plot":
            use_plot(fpath)


def set_pause(var: tk.StringVar):
    global pause_time

    pause_time = int(var.get())


# default_dims = "400x523+16+18"

default_dims = ""
style2 = sttk.create_styles()

viewport = {'w': 400, 'h': 300, 'gutter': 10}
my_pady = 10

canv_1 = tk.Canvas(root,
                   width=viewport['w'],
                   height=viewport['h'],
                   highlightthickness=0,
                   background='green')
canv_1.pack(fill='both', expand=True)
canv_1.configure(width=viewport['w'], height=viewport['h'])
canv_1.bind('<Configure>', lambda ev, vp=viewport: cnv_ui.resize_viewport(ev, vp))
# canv_1.update()
# print(f'{canv_1.winfo_width()=}, {canv_1.winfo_height()=}')

textvar = tk.StringVar()
caption = ttk.Entry(root, justify='center', textvariable=textvar)
caption.pack(fill='x', expand=True)
caption.update()

open_button = ttk.Button(root, text="Open Files", command=lambda c=canv_1: open_image_file(c))
open_button.pack(pady=my_pady)

ui_fr = ttk.Frame(root, relief='groove', style='alt.TFrame')

display_pause = tk.StringVar(value='3')
enter_display_pause = sel.EntryFrame(ui_fr,
                                     display_name='Pause',
                                     name='pause',
                                     posn=[0],
                                     stick='w',
                                     var=display_pause,
                                     callb=lambda var=display_pause: set_pause(var)
                                     )

but_reset_size = ttk.Button(ui_fr, text="reset window size",
                            command=lambda canv=canv_1,
                                           # dims=default_dims,
                                           vp=viewport: reset_window_size(canv, vp),
                            style="MyButton1.TButton")
but_reset_size.pack(padx=5, pady=my_pady)

ui_fr.pack(side='top', ipadx=5, ipady=5, padx=5, pady=5)
ui_fr.update()

btnq = ttk.Button(root,
                  text="Quit",
                  command=root.quit,
                  style="MyButton1.TButton")
btnq.pack(side="top", pady=my_pady)
btnq.update()

# show some layout dimensions
# ----
# print(f'canv_static1 h,w: {canv_static1.winfo_height()}, {canv_static1.winfo_width()}')
# print(f'ui_fr h,w: {ui_fr.winfo_height()}, {ui_fr.winfo_width()}')
# print(f'lab h,w: {lab.winfo_height()}, {lab.winfo_width()}')

# update widget sizes
# print(f'{root.geometry()=}')
total_ht = canv_1.winfo_height() + caption.winfo_height() + open_button.winfo_height() + ui_fr.winfo_height() + btnq.winfo_height()
# print(f'{total_ht=}')
# total_wd = max(lab.winfo_width(), canv_dyn1.winfo_width(), ui_fr.winfo_width())
total_wd = max(canv_1.winfo_width(), ui_fr.winfo_width())
# default_dims = f'{total_wd}x{total_ht}'
default_dims = root.geometry()

# root.minsize(total_wd, total_ht)
root.minsize(400, 474)
print(f'{root.geometry()=}')

if __name__ == "__main__":
    root.mainloop()
