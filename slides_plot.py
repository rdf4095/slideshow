"""
program: slides_plot.py

purpose: For project slideshow.

comments: Demonstrates the display of one or more images in succession,
          using matplotlib.

          No Artificial Intelligence was used in production of this code.

author: Russell Folks

history:
-------
12-10-2025  Extracted from the original main file that used a flag to run
            either this method or the Canvas method of image display
03-24-2026  Begin phasing out the canvas object; Remove resize_and_update().
04-04-2026  Disable code related to image display.
04-09-2026  New approach to displaying image list: Frame/Label & Text.
            Still developing spacing of these Frames.
04-13-2026  Debug the approach to displaying lists of files for each show.
            Remove some old code: variables, tests and comments.
04-14-2026  Remove old code, update some comments.
04-15-2026  Change display_to_plot() to display_slides().
            New logic for resuming a paused show: add flag to display_slides.
04-17-2026  Debug pause/resume when there are multiple shows.
04-22-2026  Debug restart of the show.
"""
import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader
import time
import tkinter.font as tkfont

from ttkthemes import ThemedTk
from PIL import Image
import matplotlib.pyplot as plt

# ? attempt to retain focus; what does this do to the pause/resume
plt.rcParams["figure.raise_window"]=False

sttk = SourceFileLoader("styles_ttk", "../styles/styles_ttk.py").load_module()
cnv_ui = SourceFileLoader("cnv_ui", "../canvas/canvas_ui.py").load_module()
sel = SourceFileLoader("ui", "../utilities/tool_classes.py").load_module()

root = ThemedTk()
root.resizable(True, True)
root.title("canvas, ttk, pack")

# ? can all of these vars be moved below the function defs
delay_time = 3

helv12 = tkfont.Font(family='Helvetica', size=12)
helv12b = tkfont.Font(family='Helvetica', size=12, weight='bold')

# which of these is necessary?
# canv_config_flag = False
enter_canvas_flag = False
leave_canvas_flag = False
in_window = True

def reset_window_size(canv: object, vp: dict) -> None:
    """Reset the app main window to the global default_dims size."""
    root.geometry(default_dims)


def select_image_files(canv: object) -> None:
    if run_status is True:
        file_path = filedialog.askopenfilenames(title="Select Images for Display",
                                                initialdir="images",
                                                filetypes=[("Png files", "*.png"),
                                                           ("Jpeg files", "jpg"),
                                                           ("All files", "*.*")]
                                                )
        if file_path:
            setup_plot(file_path)


def setup_plot(fpath: tuple | str) -> None:
    """Display a sequence of images using matplotlib.

    Uses module variables:
        canv_1
        helv12
        helv12b

    Notes:
        1. The isinstance test is only needed if path is passed in as a string.
           There is currently no code to do this.
        2. The figure object is only needed to suppress the window UI widgets
           using pack_forget().
        3. This method does not support the 'with' context manager for reading files.
        4. This method is easier for +1 independent slideshow (using different figures).
    """
    global image_objects
    global images_opened
    global run_status
    global canv_1
    global list_frames

    # re-init globals
    image_objects = []
    images_opened = []

    if isinstance(fpath, str):
        print('converting path string to tuple...')
        fpath = (fpath,)

    # debug
    # Using an explicit number (the 1 in this case), enables us to return to
    # that figure later.
    # ...or can we find it based on its close event?
    # fig = plt.figure(1, figsize=[9.6, 5.0], clear=True)

    # With no figure number specified, a new figure is automatically created.
    existing_figs = plt.get_fignums()    # list
    fig = plt.figure(figsize=[9.6, 5.0], clear=True)

    # ?
    # fig.add_callback(on_close())
    fig.canvas.mpl_connect('close_event', on_close)

    # Title for the list
    figures = plt.get_fignums()
    figure_text = 'Figure ' + str(figures[-1])

    # nam = 'list' + str(figures[-1])
    # disp_nam = 'list ' + str(figures[-1])

    for n, item in enumerate(fpath):
        try:
            im = Image.open(item)
            images_opened.append(item)
            image_objects.append(im)
        except Exception as e:
            print(f'error opening image: {str(e)}')

    num_to_show = len(images_opened)

    fr = tk.Frame(canv_1, width=400)
    list_label = tk.Label(fr, text=figure_text, background='cyan')
    list_label.pack(anchor='w')

    t1 = tk.Text(fr, height=num_to_show)
    t1.pack(anchor='w')

    list_frames.append(fr)

    display_slides(fr, 0)


def display_slides(fr: object,
                   startnum=0,
                   resume=False,
                   restart=False) -> None:
    # since this will be used for initial display, and add_to_slides will be
    # used to resume the paused show, startnum here can be assumed to be 0 (?).

    # need fewer globals, or more parameters, or some other way...
    global image_objects
    global images_opened
    global images_selected
    global run_status
    global canv_windows
    global canv_1

    print('in display_slides')
    print(f'    {startnum=}')
    root.focus()

    # print(f'    {resume=}')
    t1 = fr.winfo_children()[1]
    if restart is True:
        # print('restart')
        # print(f'{t1['state']=}')
        # t1.config(state='normal')
        # print(f'{t1['state']=}')
        t1.delete('1.0', 'end')
    else:
        if resume is False:
            win_y = 2
            if len(canv_windows) > 0:
                item = canv_windows[-1]

                bbox = canv_1.canv.bbox(item)
                print(f'    {bbox=}')
                win_y = bbox[3] + 5

            thiswin = canv_1.canv.create_window(200, win_y, anchor=tk.N, width=400, window=fr)
            canv_windows.append(thiswin)

    images_selected = []

    for n, item in enumerate(image_objects[startnum:], startnum):
        if run_status is True:
            plt.clf()
            # imshow creates the matplotlib Artist "AxesImage" in the container "ax.images"
            plt.imshow(item)
            plt.axis("off")

            filename = images_opened[n].split('/')[-1]
            images_selected.append(filename)

            item_text = str(n + 1) + ': ' + filename
            # figures = plt.get_fignums()
            # thisname = 'list' + str(figures[-1]) + '_canvas'

            # check for dupe line:
            # if item_text == t1.get(float(startnum), 'end - 2c'):
            #     skip insert
            # END check

            t1.insert('end', item_text)
            t1.insert('end', '\n')

            plt.title('image ' + item_text)
            plt.pause(3)
        else:
            break


# Might not need this (as alternative to display_slides when resuming a paused show.)
# def add_to_slides(fr: object,
#                   startnum=0) -> None:
#     pass


def set_delay(var: tk.StringVar) -> None:
    global delay_time

    delay_time = int(var.get())


def pause_show(ev):
    """uses module objects:

    images_opened, image_objects
    """
    print(f'in pause_show')
    global run_status

    run_status = False


def resume_show(ev) -> None:
    global images_opened
    global images_selected
    global run_status

    run_status = True
    print(f'in resume_show')

    thisnum = 0

    # get the most recent Frame
    # children = root.winfo_children()
    # frames = [i for i in children if i.__class__ == ttk.Frame]
    thisnum = len(images_selected)
    print(f'    {len(images_opened)=}')
    print(f'    {len(images_selected)=}')
    # cfr = frames[0].winfo_children()[-1]
    cfr = list_frames[-1]

    # print('resume_show:')
    # print(f'    {frames[0]=}, {type(frames[0])=}')
    # print(f'    {cfr=}, {type(cfr)=}')
    display_slides(cfr, thisnum, resume=True)


def restart_slides(canv: object) -> None:
    # global images_opened
    # global images_selected
    global run_status

    print(f'in restart_slides...')
    children = canv_1.winfo_children()
    frames = [i for i in children if i.__class__ == tk.Frame]
    fr = frames[-1]

    run_status = True
    thisnum = 0

    display_slides(fr, thisnum, restart=True)


def step_forward(ev):
    """Display the next image in the current show list"""
    print(f'in step_forward, {ev=}')
    if run_status == False:
        pass


def step_back(ev):
    """Display the previous image in current show list."""
    print(f'in step_back, {ev=}')
    if run_status == False:
        pass


def get_list_display(ev):
    # print(f'in get_list_display, {ev=}')
    pass


def on_close(ev):
    # print(f'in on_close, {ev=}')
    # _number is used in the default window title, and as a unique number for
    # the matplotlib figure object.
    # Although we could access this protected attribute to determine the figure
    # that was closed, we still need to keep track of the figure number as a
    # global var so that the corresponding canvas_window can be deleted.
    # print(f'    {ev.canvas.figure._number=}')
    pass


def set_enter_canvas(ev):
    # pass
    enter_canvas_flag = True
    root.focus()
    # print(f'in set_enter_canvas:\n    {enter_canvas_flag=}, {leave_canvas_flag=}')


def set_leave_canvas(ev):
    # pass
    leave_canvas_flag = True
    # print(f'in set_leave_canvas:\n    {enter_canvas_flag=}, {leave_canvas_flag=}')


# default_dims = "400x523+16+18"
default_dims = ""
style2 = sttk.create_styles()

viewport = {'w': 400, 'h': 300, 'gutter': 10}
my_pady = 10
run_status=True

# ? are all 3 of these lists necessary
images_selected = []
images_opened = []
image_objects = []

canv_windows = []
list_frames = []


canv_1 = sel.CanvasFrame(root,
                         name='canv_1',
                         display_name='slideshows',
                         posn=[1],
                         stick='nsew')
canvas = canv_1.canv

# what's the purpose?
canv_1.master.bind('<Leave>', set_leave_canvas)
canv_1.master.bind('<Enter>', set_enter_canvas)

# can probably keep this (no need for root.bind...
# canv_1.master.bind('<Control-Down>',
#                    lambda ev: pause_show(ev)
#                    )
# canv_1.master.bind('<Control-Up>',
#                    lambda ev,
#                           canv=canv_1: resume_show(ev, canv)
#                    )
root.bind_all('<Control-Down>',
                   lambda ev: pause_show(ev)
                   )
# root.bind_all('<Control-Up>',
#                    lambda ev,
#                           canv=canv_1.canv: resume_show(ev, canv)
#                    )
root.bind_all('<Control-Up>',
                   lambda ev: resume_show(ev)
                   )

textvar = tk.StringVar()
caption = ttk.Entry(root, justify='center', textvariable=textvar)
caption.pack(fill='x', expand=True)
caption.update()

open_button = ttk.Button(root, text="Open Files", command=lambda c=canv_1: select_image_files(c))
open_button.pack(pady=my_pady)

ui_fr = ttk.Frame(root, relief='groove', style='alt.TFrame')

delay = tk.StringVar(value='3')
enter_delay_time = sel.EntryFrame(ui_fr,
                                  display_name='Delay',
                                  name='delay',
                                  posn=[0],
                                  stick='w',
                                  var=delay,
                                  callb=lambda var=delay: set_delay(var)
                                  )

restart_show = ttk.Button(ui_fr, text="restart show",
                          style="MyButton1.TButton",
                          command = lambda canv=canv_1: restart_slides(canv))
restart_show.pack(ipadx=5, ipady=0, padx=5, pady=5)

window_reset = ttk.Button(ui_fr, text="reset window size",
                          command=lambda canv=canv_1,
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

total_ht = canv_1.winfo_height() + caption.winfo_height() + open_button.winfo_height() + ui_fr.winfo_height() + btnq.winfo_height()
total_wd = max(canv_1.winfo_width(), ui_fr.winfo_width())

# begin test: show some layout dimensions ----------
# print(f'canv_static1 h,w: {canv_static1.winfo_height()}, {canv_static1.winfo_width()}')
# print(f'ui_fr h,w: {ui_fr.winfo_height()}, {ui_fr.winfo_width()}')
# print(f'lab h,w: {lab.winfo_height()}, {lab.winfo_width()}')

# print(f'{root.geometry()=}')

# print(f'{total_ht=}')
# total_wd = max(lab.winfo_width(), canv_dyn1.winfo_width(), ui_fr.winfo_width())
# default_dims = f'{total_wd}x{total_ht}'
# ---------- END test

default_dims = root.geometry()

# root.minsize(total_wd, total_ht)
root.minsize(400, 474)

if __name__ == "__main__":
    root.mainloop()
