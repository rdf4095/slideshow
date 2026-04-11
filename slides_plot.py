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
"""
import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader
import time
import tkinter.font as tkfont

from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
# ? needed
from matplotlib.pyplot import figure

# ? attempt to retain focus; what does this do to the pause/resume
plt.rcParams["figure.raise_window"]=False

sttk = SourceFileLoader("styles_ttk", "../styles/styles_ttk.py").load_module()
cnv_ui = SourceFileLoader("cnv_ui", "../canvas/canvas_ui.py").load_module()
sel = SourceFileLoader("ui", "../utilities/tool_classes.py").load_module()

root = ThemedTk()
root.resizable(True, True)
root.title("canvas, ttk, pack")

delay_time = 3

helv12 = tkfont.Font(family='Helvetica', size=12)
helv12b = tkfont.Font(family='Helvetica', size=12, weight='bold')

# which of these is necessary?
canv_config_flag = False
enter_canvas_flag = False
leave_canvas_flag = False
in_window = True

def reset_window_size(canv: object, vp: dict) -> None:
    """Reset the app main window to the global default_dims size."""
    pass


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
    global lens_image_objects
    global run_status
    global canv_1
    global previous_ht

    # re-init globals
    image_objects = []
    images_opened = []

    if isinstance(fpath, str):
        print('converting path string to tuple...')
        fpath = (fpath,)

    # debug
    # Using an explicit number (the 1 in this case), enables us to return to
    # that figure later.
    # fig = plt.figure(1, figsize=[9.6, 5.0], clear=True)

    # With no figure number specified, a new figure is automatically created.
    existing_figs = plt.get_fignums()    # list
    fig = plt.figure(figsize=[9.6, 5.0], clear=True)
    # fig.add_callback(on_close())
    fig.canvas.mpl_connect('close_event', on_close)

    line_height = 18
    fig_offset = line_height * 2

    factor = len(existing_figs) * fig_offset
    list_offset = (len(lens_image_objects) * line_height) + factor

    # Display a title for the list
    figures = plt.get_fignums()
    figure_text = 'Figure ' + str(figures[-1])

    nam = 'list' + str(figures[-1])
    disp_nam = 'list ' + str(figures[-1])

    figure_row = len(existing_figs)

    for n, item in enumerate(fpath):
        try:
            im = Image.open(item)
            images_opened.append(item)
            image_objects.append(im)
        except Exception as e:
            print(f'error opening image: {str(e)}')

        # update spacing for next list, if any
        lens_image_objects.append(len(item))

    # new
    num_to_show = len(images_opened)
    calc_ht = (line_height * num_to_show) + 19    # 9 = pady + (linespacing = 2) * 2
    fr = tk.Frame(canv_1, width=400, height=calc_ht)
    list_label = tk.Label(fr, text=figure_text)
    list_label.pack(anchor='w', pady=5)
    list_label.update()
    label_ht = list_label.winfo_height()
    print(f'{label_ht=}')
    calc_ht += (23 + 15)
    previous_ht += (label_ht + 15)
    # END new

    display_to_plot(calc_ht, fr, 0)


def display_to_plot(list_offset: int,
                    fr: object,
                    startnum=0) -> None:
    global image_objects
    global images_opened
    global run_status
    global previous_ht

    h_offset = 6
    v_offset = 6
    line_height = 30    # 20 + linespacing=2 + linespacing=2

    print('in display_to_plot')
    root.focus()

    t1 = tk.Text(fr, pady=5, spacing3=2)
    t1.pack(anchor='w', pady=5)
    text_win_ht = line_height * len(images_opened) + 5
    # calc_ht = text_win_ht + v_offset
    print(f'    {previous_ht=}')
    print(f'    {text_win_ht=}')
    print(f'    {list_offset=}')
    textwin = canv_1.canv.create_window(200, previous_ht, anchor=tk.N, width=400, height=list_offset, window=fr)

    previous_ht = list_offset

    for n, item in enumerate(image_objects[startnum:], startnum):
        if run_status is True:
            plt.clf()
            # imshow creates the matplotlib Artist "AxesImage" in the container "ax.images"
            plt.imshow(item)
            plt.axis("off")

            filename = images_opened[n].split('/')[-1]
            images_selected.append(filename)

            item_text = str(n + 1) + ': ' + filename
            text_x = h_offset
            # text_y = (n * line_height) + line_height + (v_offset * 2) + list_offset
            text_y = (n * line_height) + (v_offset * 2) + list_offset

            figures = plt.get_fignums()
            thisname = 'list' + str(figures[-1]) + '_canvas'

            # cnv = fr.__dict__["children"][thisname]

            # NOTE: should probably directly call create_text
            # add_text(cnv, item_text, (text_x, text_y))
            # container.create_text(xy[0], xy[1], anchor='w', font='helv12', text=item_text)

            t1.insert('end', item_text)
            # ? should not be necessary to insert a newline
            t1.insert('end', '\n')

            plt.title('image ' + item_text)
            plt.pause(3)
        else:
            break


# def add_text(container: object,
#              line: str,
#              xy: tuple) -> None:
#     print('in add_text...')
#     print(f'    in container: {container}')
#     print(f'    writing text: {line}')
#     print(f'    to: {xy}')
#
#     container.create_text(xy[0], xy[1], anchor='w', font='helv12', text=line)


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


def resume_show(ev, canv: object) -> None:
    global images_opened
    global images_selected
    global run_status

    run_status = True
    print(f'in resume_show')

    thisnum = 0

    # else:

    # get the most recent Frame
    children = root.winfo_children()
    frames = [i for i in children if i.__class__ == ttk.Frame]

    thisnum = len(images_selected)

    cfr = frames[0].winfo_children()[-1]

    # print('resume_show:')
    # print(f'    {frames[0]=}, {type(frames[0])=}')
    # print(f'    {cfr=}, {type(cfr)=}')
    display_to_plot(0, cfr, thisnum)


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
    pass


def read_but1(ev, vp):
    print(f'in read_but1: {ev}')

    # cnv_ui.resize_viewport(ev, vp)
    canv = ev.widget

    if len(images_opened) == 0:
        return
    # ? slow
    # ...proceed with setting startnum (the zero in this call)
    thisnum = 0
    for n, item in enumerate(canv.find_all()):
        if canv.itemcget(item, "state") == "normal":
            thisnum = n
            break  # only one is normal

    # try
    im = Image.open(images_opened[-1])
    params = cnv_ui.calc_resize_to_vp(viewport, im)
    canv.configure(width=params['wid_int'], height=params['ht_int'])
    canv.update()
    # END try

    # use_canvas(canv, tuple(images_opened), thisnum)


def set_enter_canvas(ev):
    # pass
    enter_canvas_flag = True
    in_window = True
    root.focus()
    # print(f'in set_enter_win:\n    {canv_config_flag=}, {enter_canvas_flag=}, {leave_canvas_flag=}')


def set_leave_canvas(ev):
    # pass
    leave_canvas_flag = True
    in_window = False
    # print(f'in set_leave_win:\n    {canv_config_flag=}, {enter_canvas_flag=}, {leave_canvas_flag=}')


# default_dims = "400x523+16+18"
default_dims = ""
style2 = sttk.create_styles()

viewport = {'w': 400, 'h': 300, 'gutter': 10}
my_pady = 10
previous_ht = 0
run_status=True
images_selected = []
images_opened = []
image_objects = []
lens_image_objects = []


canv_1 = sel.CanvasFrame(root,
                         name='canv_1',
                         display_name='slideshows',
                         posn=[1],
                         stick='nsew')
# test
# ----
# canvas = canv_1.winfo_children()[1]
canvas = canv_1.canv

# try, instead of canvas with windows/frames/text_objects
# scr_win = ttk.PanedWindow()

# begin test
# ----------
# lines = ['one', 'two', 'three', 'four', 'five', 'six', 'seven']
# show1 = 4
# calc_ht1 = (show1 * 19) + 5 + 2
# fr1 = tk.Frame(canvas, width=400, height=calc_ht1)
# # Text defaults to the width of the container
# t1 = tk.Text(fr1, pady=5, spacing3=2)
# for n, i in enumerate(lines[0:show1]):
#     t1.insert('end', i)
#     # ? should not be necessary to insert a newline
#     t1.insert('end', '\n')
# t1.pack(pady=5)
# twin1 = canvas.create_window(200, 0, anchor=tk.N, width=400, height=calc_ht1, window=fr1)
#
# fr2 = tk.Frame(canvas, width=400, height=100)
# t2 = tk.Text(fr2, pady=5, spacing3=2)
# show2 = 5
# calc_ht2 = (show2 * 19) + 5 + 2
# for n, i in enumerate(lines[0:show2]):
#     t2.insert('end', i)
#     t2.insert('end', '\n')
# t2.pack(pady=5)
# twin2 = canvas.create_window(200, calc_ht1, anchor=tk.N, width=400, height=calc_ht2, window=fr2)
#
# fr3 = tk.Frame(canvas, width=400, height=100)
# t3 = tk.Text(fr3, pady=5, spacing3=2)
# show3 = 3
# calc_ht3 = (show3 * 19) + 5 + 2
# for n, i in enumerate(lines[0:show3]):
#     t3.insert('end', i)
#     t3.insert('end', '\n')
# t3.pack(pady=5)
# twin3 = canvas.create_window(200, calc_ht1 + calc_ht2, anchor=tk.N, width=400, height=calc_ht3, window=fr3)

# END test



# canv_1.bind('<Configure>', lambda ev,
#                                   vp=viewport,
#                                   f=canv_config_flag: cnv_ui.resize_viewport(ev, vp, f))

canv_1.bind('<Button-1>', lambda ev, vp=viewport: read_but1(ev, vp))

# works, but what's the purpose?
canv_1.master.bind('<Enter>', set_enter_canvas)
canv_1.master.bind('<Leave>', set_leave_canvas)

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
root.bind_all('<Control-Up>',
                   lambda ev,
                          canv=canv_1: resume_show(ev, canv)
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

# begin test: show some layout dimensions
# ----------
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

# END test
# --------

default_dims = root.geometry()

# root.minsize(total_wd, total_ht)
root.minsize(400, 474)

if __name__ == "__main__":
    root.mainloop()
