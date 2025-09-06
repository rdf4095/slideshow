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
08-23-2025  Split canvas method into 1) load images, 2) create on canvas.
            Change images by setting canvas.image.
08-26-2025  Debug pause_show and resume_show. Add to plot method: display of
            filename in title, and in canvas. Rename fxn but_reset_size
            to window_reset.
08-30-2025  Debug pause_show to delete previous image.
"""
"""
TODO:
    1. If window is dragged larger, then image is displayed, then reset button is clicked,
       image is not resized. This requires delete() followed by re-display. Need to get
       which image it is...
    2. ? Always use the matplotlib method. Resserve the main window for 
       housekeeping (image lists & info, slideshow lists, etc.)
       Main window could also be minimal, and expand if more info is needed.
"""
import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader
import time
import tkinter.font as tkfont
import resource

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
# font_hu = tkfont.Font(family='Helvetica', size=14, weight='bold', underline=1)
helv12 = tkfont.Font(family='Helvetica', size=12)
helv12b = tkfont.Font(family='Helvetica', size=12, weight='bold')

def using(point=""):
    usage=resource.getrusage(resource.RUSAGE_SELF)
    return '''%s: usertime=%s systime=%s mem=%s mb
           '''%(point,usage[0],usage[1],
                usage[2]/1024.0 )


# def reset_window_size(canv: object, dims: str, vp) -> None:
def reset_window_size(canv: object, vp) -> None:
    """Reset the app main window to the global default_dims size."""
    root.geometry(default_dims)

    canv.configure(width=400, height=300)
    vp['w'] = 400
    vp['h'] = 300

    # canv.delete('image')
    canv.configure(width=vp['w'], height=vp['h'])


def select_image_file(canv: object):
    # global but_reset_size

    if run_status is True:
        file_path = filedialog.askopenfilenames(title="Select Image File",
                                                initialdir="images",
                                                filetypes=[("Png files", "*.png"),
                                                           ("Jpeg files", "jpg"),
                                                           ("All files", "*.*")]
                                                )
        if file_path:
            add_image(canv, file_path)
        window_reset.focus_set()


def use_canvas(canv: object,
               fpath: tuple | str,
               startnum: int=0) -> None:
    # new module variables
    # if the last image should persist, enable this line:
    global im_tk

    # existing module variables
    global image_objects
    global image_opened

    image_objects = []
    if isinstance(fpath, str):
        fpath = (fpath, )

    for n, item in enumerate(fpath):
        # if run_status is True:
            try:
                with Image.open(item) as im:
                    imsize = cnv_ui.init_image_size(im, viewport)
                    im_resize = im.resize((imsize['w'], imsize['h']))

                    im_tk = ImageTk.PhotoImage(im_resize)
                    image_objects.append(im_tk)
                    images_opened.append(im.filename)

                    # print(f'added {im.filename} to images_opened')
                    # test
                    # print(f'{canv.itemcget('image', 'image')=}')
            except Exception as e:
                print(f'error opening image: {str(e)}')

    # print(f'{images_opened=}')
    # print(f'{fpath=}')

    display_to_canvas(canv, fpath, startnum)


def display_to_canvas(canv, pathlist, startnum):
    """Uses these variables from the module scope
    (should we pass them in?):

        pause_time
        textvar
        images_selected
    """
    global image_objects
    global images_opened
    global run_status
    allids = None

    for n, item in enumerate(image_objects[startnum:]):#, startnum):
        centered_x = viewport['w'] / 2
        centered_y = viewport['h'] / 2

        if run_status is True:
            imid = canv.create_image(centered_x, centered_y, image=item, tag='image')#, state=tk.HIDDEN)
            print(f'creating {imid=}')
            fname = images_opened[n].split('/')[-1]
            images_selected.append(fname)
            lab = str(n + 1) + ' of ' + str(len(pathlist)) + ': ' + fname
            textvar.set(lab)

        # if run_status is True:
            allids = canv.find_all()
            print(f'{allids=}')
            # for n, i in enumerate(allids[:-1]):
            #     print(f'deleting: {allids[n]}')
            #     canv.delete(allids[n])

            canv.update()
            time.sleep(pause_time)
            canv.itemconfigure(allids[n], state=tk.HIDDEN)

        else:
            print(f'else: {run_status}')
            break

    # unhide the last image
    canv.itemconfigure(allids[-1], state=tk.NORMAL)


def use_plot(fpath: tuple | str):
    """Display a sequence of images using matplotlib.

    Uses the module variables:
        canv_1
        helv12
        helv12b

    Notes:
        1. The isinstance test is only needed if path is passed in as a string.
           There is currently no code to do this.
        2. The figure object is only needed to suppress the window UI widgets
           using pack_forget().
        3. This method does not support the 'with' context manager for reading files.
        4. This method is probably the easier way to have more than one
           independent slideshow (using different figures).
    """
    global image_objects
    global images_opened
    global lens_image_objects
    global run_status

    if isinstance(fpath, str):
        print('converting path string to tuple...')
        fpath = (fpath,)

    # debug
    # nums = plt.get_fignums()    # list
    # print(f'starting {nums=}')   # empty list, if none

    # Using an explicit number (the 1 in this case), enables us to return to
    # that figure later.
    # fig = plt.figure(1, figsize=[9.6, 5.0], clear=True)

    # With no figure number specified, a new figure is automatically created.
    fig = plt.figure(figsize=[9.6, 5.0], clear=True)

    fig_nums = plt.get_fignums()    # list
    h_offset = 6
    v_offset = 6
    v_line = 18
    fig_offset = v_line * 2
    if len(lens_image_objects) > 0:
        figure_offset = (sum(lens_image_objects) * v_line) + (fig_offset)
    else:
        # zero (first line)
        figure_offset = sum(lens_image_objects)

    # canv_1.delete('file_list')

    # heading for the list
    figure_text = 'Figure ' + str(fig_nums[-1])
    canv_1.create_text(h_offset, v_offset + figure_offset, text=figure_text, font=helv12b, anchor='nw', tag='file_list')

    for n, item in enumerate(fpath):
        # if run_status is True:
        try:
            im = Image.open(item)
            images_opened.append(item)
            image_objects.append(im)
            # plt.clf()
            # plt.imshow(im)
            # plt.axis("off")
            # filename = item.split('/')[-1]
            #
            # item_text = str(n+1) + ': ' + filename
            # text_x = h_offset
            # text_y = n * v_line + v_line + (v_offset * 2) + figure_offset
            # canv_1.create_text(text_x, text_y, text=item_text, font=helv12, anchor='nw', tag='file_list')
            #
            # plt.title('image ' + item_text)
            # # fig.canvas.toolbar.pack_forget()
            # plt.pause(3)
        except Exception as e:
            print(f'error opening image: {str(e)}')

        # update spacing for next list, if any
        lens_image_objects.append(len(item))

    display_to_plot(fpath, 0)


def display_to_plot(pathlist, startnum=0):
    global image_objects
    global images_opened
    global run_status

    # temp
    h_offset = 6
    v_offset = 6
    v_line = 18
    figure_offset = 0

    for n, item in enumerate(image_objects[startnum:], startnum):
        if run_status is True:
            plt.clf()
            plt.imshow(item)
            plt.axis("off")
            filename = images_opened[n].split('/')[-1]
            images_selected.append(filename)

            item_text = str(n + 1) + ': ' + filename
            text_x = h_offset
            text_y = n * v_line + v_line + (v_offset * 2) + figure_offset
            canv_1.create_text(text_x, text_y, text=item_text, font=helv12, anchor='nw', tag='file_list')

            plt.title('image ' + item_text)
            # fig.canvas.toolbar.pack_forget()
            plt.pause(3)


def add_image(canv: object, fpath: tuple | str):
    global display_method

    match display_method:
        case "canvas":
            use_canvas(canv, fpath)
        case "plot":
            use_plot(fpath)


def set_delay(var: tk.StringVar):
    global pause_time

    pause_time = int(var.get())


def pause_show(ev):
    """uses module objects:

    images_opened, image_objects
    """
    global run_status

    run_status = False
    print(f'in pause_show')
    print(f'    images shown: {len(images_selected)}, last: {images_selected[-1]}')
    # files = [i.split('/')[-1] for i in images_opened]
    # print(f'    {files=}')
    # print(f'    {len(image_objects)=}')


def resume_show(ev, canv):
    global images_opened
    global images_selected
    global run_status
    global display_method

    run_status = True
    print(f'in resume_show')
    num = len(images_selected)
    print(f'    next: {image_objects[num]} ({images_opened[num]})')

    if display_method == 'canvas':
        # remove any displayed images
        canv.delete(num)
        display_to_canvas(canv, tuple(images_opened), num)
    else:
        display_to_plot(tuple(images_opened), num)


# default_dims = "400x523+16+18"

default_dims = ""
style2 = sttk.create_styles()

viewport = {'w': 400, 'h': 300, 'gutter': 10}
my_pady = 10
run_status=True
images_selected = []
images_opened = []
image_objects = []
lens_image_objects = []
# test resources
print(using('before'))
# END test
wrk = ['waste'] * 1000000
# test resources
print(using('after'))
# END test

canv_1 = tk.Canvas(root,
                   width=viewport['w'],
                   height=viewport['h'],
                   highlightthickness=0,
                   background='green')
canv_1.pack(fill='both', expand=True)
canv_1.configure(width=viewport['w'], height=viewport['h'])
canv_1.bind('<Configure>', lambda ev, vp=viewport: cnv_ui.resize_viewport(ev, vp))
canv_1.master.bind('<Control-Down>',
                   lambda ev: pause_show(ev)
                   )
canv_1.master.bind('<Control-Up>',
                   lambda ev,
                          canv=canv_1: resume_show(ev, canv)
                   )

# canv_1.update()
# print(f'{canv_1.winfo_width()=}, {canv_1.winfo_height()=}')

textvar = tk.StringVar()
caption = ttk.Entry(root, justify='center', textvariable=textvar)
caption.pack(fill='x', expand=True)
caption.update()

open_button = ttk.Button(root, text="Open Files", command=lambda c=canv_1: select_image_file(c))
open_button.pack(pady=my_pady)

ui_fr = ttk.Frame(root, relief='groove', style='alt.TFrame')

delay = tk.StringVar(value='3')
enter_delay_time = sel.EntryFrame(ui_fr,
                                  display_name='Pause',
                                  name='pause',
                                  posn=[0],
                                  stick='w',
                                  var=delay,
                                  callb=lambda var=delay: set_delay(var)
                                  )

window_reset = ttk.Button(ui_fr, text="reset window size",
                          command=lambda canv=canv_1,
                                           # dims=default_dims,
                                           vp=viewport: reset_window_size(canv, vp),
                          style="MyButton1.TButton")
window_reset.pack(padx=5, pady=my_pady)

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
# print(f'{root.geometry()=}')

if __name__ == "__main__":
    root.mainloop()
