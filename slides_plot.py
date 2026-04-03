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

# display_method can have two values:
# canvas = python canvas
# plot   = matplotlib.show
# display_method = "plot"
delay_time = 3

helv12 = tkfont.Font(family='Helvetica', size=12)
helv12b = tkfont.Font(family='Helvetica', size=12, weight='bold')

# test
canv_config_flag = False
enter_win_flag = False
leave_win_flag = False
in_window = True
# END test

def reset_window_size(canv: object, vp: dict) -> None:
    """Reset the app main window to the global default_dims size."""
    # This won't restore the size if the window has been manually
    #  dragged to a new size.

    # an example of setting a size, or selecting a size from a list
    # fig = plt.gcf()
    # fig.set_size_inches(10.6 ,6.0, forward=True)
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
            add_image(canv, file_path)

        # probably doesn't do anything...
        root.focus()


# def use_canvas(canv: object,
#                fpath: tuple | str,
#                startnum: int=0
#                ) -> None:
#     """Display a sequence of images using tk.Canvas.
#     Create a PIL PhotoImage for each file in a list of paths.
#
#     Uses module variables:
#         image_objects
#         images_opened
#
#     Calls:
#         prep_canvas
#         display_to_canvas
#     """
#     # if the last image should persist, enable this line:
#     global im_tk
#     global image_objects
#     global images_opened
#
#     image_objects = []
#     images_opened = []
#     if isinstance(fpath, str):
#         fpath = (fpath, )
#
#     for n, item in enumerate(fpath):
#             try:
#                 with Image.open(item) as im:
#                     imsize = cnv_ui.init_image_size(im, viewport)
#                     im_resize = im.resize((imsize['w'], imsize['h']))
#
#                     im_tk = ImageTk.PhotoImage(im_resize)
#
#                     image_objects.append(im_tk)
#                     images_opened.append(im.filename)
#                     # or, for consistency, do it like use_plot:
#                     # images_opened.append(item)
#
#                     # print(f'{canv.itemcget('image', 'image')=}')
#             except Exception as e:
#                 print(f'error opening image: {str(e)}')
#
#     prep_canvas(canv, startnum)
#
#     display_to_canvas(canv, fpath, startnum)


# def prep_canvas(canv: object, startnum: int) -> None:
#     """Prepare the Canvas for image display by creating the list of objects.
#     Uses these module variables:
#         image_objects
#         images_opened
#         images_selected
#     """
#     # print('in prep_canvas')
#     # print(f'    {viewport['w']=}, {viewport['h']=}')
#     # print(f'    {canv_1.winfo_width()=}, {canv_1.winfo_height()=}')
#
#     # delete any existing images
#     idlist = canv.find_all()
#     for n, item in enumerate(idlist):
#         canv.delete(item)
#
#     for n, item in enumerate(image_objects[startnum:]):#, startnum):
#         centered_x = viewport['w'] / 2
#         centered_y = viewport['h'] / 2
#
#         imid = canv.create_image(centered_x, centered_y, image=item, tag='image', state=tk.HIDDEN)
#         fname = images_opened[n].split('/')[-1]
#         images_selected.append(fname)


# def display_to_canvas(canv: object,
#                       pathlist: list,
#                       startnum: int
#                       ) -> None:
#     """Display a list of images to a Canvas, one at a time.
#
#     Uses these module variables:
#         image_objects
#         run_status
#         images_selected
#         textvar -- a string variable in the image caption
#         delay_time
#     """
#     # display first image
#     idlist = canv.find_all()
#     for n, item in enumerate(idlist):
#         canv.itemconfigure(item, state=tk.HIDDEN)
#
#     canv.itemconfigure(idlist[startnum], state=tk.NORMAL)
#     fname = images_selected[startnum]
#     lab = str(startnum + 1) + ' of ' + str(len(pathlist)) + ': ' + fname
#     textvar.set(lab)
#
#     canv.update()
#     time.sleep(delay_time)
#
#     # display any remaining images
#     if len(idlist) > 1:
#         for n, item in enumerate(image_objects[startnum + 1:], startnum + 1):
#             if run_status is True:
#                 # idlist = canv.find_all()
#                 canv.itemconfigure(idlist[n], state=tk.NORMAL)
#
#                 canv.itemconfigure(idlist[n-1], state=tk.HIDDEN)
#
#                 fname = images_selected[n]
#                 lab = str(n + 1) + ' of ' + str(len(pathlist)) + ': ' + fname
#                 textvar.set(lab)
#
#                 canv.update()
#                 time.sleep(delay_time)
#             else:
#                 break


def use_plot(fpath: tuple | str) -> None:
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

    # existing_figs = plt.get_fignums()    # list
    line_height = 18
    fig_offset = line_height * 2

    factor = len(existing_figs) * fig_offset
    list_offset = (len(lens_image_objects) * line_height) + factor

    # Display a title for the list
    figures = plt.get_fignums()
    figure_text = 'Figure ' + str(figures[-1])

    # figure_fr = add_text_frame(figure_text)
    nam = 'list' + str(figures[-1])
    disp_nam = 'list ' + str(figures[-1])

    # TODO: update posn for each show's CanvasFrame

    figure_fr = sel.CanvasFrame(report,
                                name=nam,
                                posn=[0, 0],
                                display_name=disp_nam,
                                stick='w')

    # print(f'{figure_fr.__class__=}')

    # print(f'{figure_fr.winfo_children()}')
    # for attribute, value in figure_fr.__dict__.items():
    #     print(f'    {attribute}, {value}')

    # print(f'{figure_fr.__dict__["children"]}')
    # print(f'{figure_fr.__dict__["children"]["list1_canvas"]}')


    for n, item in enumerate(fpath):
        try:
            im = Image.open(item)
            images_opened.append(item)
            image_objects.append(im)
        except Exception as e:
            print(f'error opening image: {str(e)}')

        # update spacing for next list, if any
        lens_image_objects.append(len(item))

    display_to_plot(list_offset, figure_fr, 0)


def display_to_plot(list_offset: int,
                    fr: object,
                    startnum=0) -> None:
    global image_objects
    global images_opened
    global run_status

    h_offset = 6
    v_offset = 6
    line_height = 18

    root.focus()
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
            # print(f'{n * line_height=}')
            # print(f'{v_offset * 2=}')
            # print(f'{list_offset=}')

            figures = plt.get_fignums()
            thisname = 'list' + str(figures[-1]) + '_canvas'

            # print('display_to_plot:')
            # print(f'    {fr=}, {type(fr)=}')
            # print(f'    {thisname=}')
            cnv = fr.__dict__["children"][thisname]

            add_text(cnv, item_text, (text_x, text_y))
            # print(f'{fr.__dict__["children"]["list1_canvas"]}')

            plt.title('image ' + item_text)
            # fig.canvas.toolbar.pack_forget()

            # has no effect:
            # canv_1.master.focus()
            # root.focus()
            plt.pause(3)
        else:
            break

    print('after enumerate...')
    # root.focus()


def add_text(container: object,
             line: str,
             xy: tuple) -> None:
    container.create_text(xy[0], xy[1], anchor='w', font='helv12', text=line)
    container.configure(scrollregion=container.bbox("all"))


def add_image(canv: object, fpath: tuple | str) -> None:
    # global display_method

    # match display_method:
    #     case "canvas":
    #         use_canvas(canv, fpath)
    #     case "plot":
    use_plot(fpath)


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
    # print(f'    next: {image_objects[num]} ({images_opened[num]})')

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
    # print(f'in step_forward, {ev=}')
    if run_status == False:
        pass


def step_back(ev):
    """Display the previous image in current show list."""
    # print(f'in step_back, {ev=}')
    # if run_status:
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


def set_enter_win(ev):
    # pass
    enter_win_flag = True
    in_window = True
    root.focus()
    # print(f'in set_enter_win:\n    {canv_config_flag=}, {enter_win_flag=}, {leave_win_flag=}')


def set_leave_win(ev):
    # pass
    leave_win_flag = True
    in_window = False
    # print(f'in set_leave_win:\n    {canv_config_flag=}, {enter_win_flag=}, {leave_win_flag=}')



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

canv_1 = tk.Canvas(root,
                   width=viewport['w'],
                   height=viewport['h'],
                   highlightthickness=0,
                   background='green')
canv_1.pack(fill='both', expand=True)
canv_1.configure(width=viewport['w'], height=viewport['h'])
# canv_1.bind('<Configure>', lambda ev,
#                                   vp=viewport,
#                                   f=canv_config_flag: cnv_ui.resize_viewport(ev, vp, f))

canv_1.bind('<Button-1>', lambda ev, vp=viewport: read_but1(ev, vp))

# works, but what's the purpose?
canv_1.master.bind('<Enter>', set_enter_win)
canv_1.master.bind('<Leave>', set_leave_win)

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

report = ttk.Frame(root)
report.pack(fill='both', expand=True)


# canv_1.update()
# print(f'{canv_1.winfo_width()=}, {canv_1.winfo_height()=}')

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
