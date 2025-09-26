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
09-08-2025  Re-implement display_to_canvas by setting image item state: change
            some function names.
09-09-2025  Move old display_to_canvas functions to scratch.txt. Remove global
            statements that are not needed, minor re-factor of use_canvas().
09-11-2025  Pause/resume works correctly in plot method.
09-12-2025  Image lists for more than one figure works correctly in plot method.
09-22-2025  Debug canvas method for more than one slideshow.
"""
"""
TODO:
    1. For canvas method: if window is dragged larger, then image is displayed, then reset button is clicked,
       image is not resized. This requires delete() followed by re-display. Need to get
       which image it is...This does not apply to the plot method.
    2. For plot method: ? window reset button must be programmed to reset the window.
"""
import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader
import time
import tkinter.font as tkfont

from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

# ? attempt to retain focus; what does this do to the pause/resume
plt.rcParams["figure.raise_window"]=False

sttk = SourceFileLoader("styles_ttk", "../styles/styles_ttk.py").load_module()
cnv_ui = SourceFileLoader("cnv", "../canvas/canvas_ui.py").load_module()
sel = SourceFileLoader("ui", "../utilities/tool_classes.py").load_module()

root = ThemedTk()
root.resizable(True, True)
root.title("canvas, ttk, pack")

# display_method can have two values:
# canvas = python canvas
# plot   = matplotlib.show
display_method = "canvas"
delay_time = 3

helv12 = tkfont.Font(family='Helvetica', size=12)
helv12b = tkfont.Font(family='Helvetica', size=12, weight='bold')


def reset_window_size(canv: object, vp) -> None:
    """Reset the app main window to the global default_dims size."""
    root.geometry(default_dims)

    canv.configure(width=400, height=300)
    vp['w'] = 400
    vp['h'] = 300

    canv.configure(width=vp['w'], height=vp['h'])

    if display_method == "plot":
        # works
        # fig = plt.gcf()

        # show the default window size
        # print(f'{fig=}')

        # This works to set the size, but won't restore the size if the window
        # has been manually dragged to a new size.
        # So, it's of no use to "reset" the window, but could be used
        # to *set* a size, or select a size from a list...

        # Also, don't do this after pausing a show; the previous images
        # will show through on the same figure.

        # works with gcf aoove
        # fig.set_size_inches(9.6 ,5.0, forward=True)

        plt.close()
        fig = plt.figure(figsize=[9.6, 5.0], clear=True)


def select_image_file(canv: object) -> None:
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
               startnum: int=0
               ) -> None:
    """Use Canvas to display images. Create a PIL PhotoImage for each file
    in a list of paths. Call other functions to handle actual display.

    Uses module variables:
        image_objects
        images_opened
    """
    # if the last image should persist, enable this line:
    global im_tk
    global image_objects
    global images_opened

    image_objects = []
    images_opened = []
    if isinstance(fpath, str):
        fpath = (fpath, )

    for n, item in enumerate(fpath):
            try:
                with Image.open(item) as im:
                    imsize = cnv_ui.init_image_size(im, viewport)
                    im_resize = im.resize((imsize['w'], imsize['h']))

                    im_tk = ImageTk.PhotoImage(im_resize)
                    image_objects.append(im_tk)
                    images_opened.append(im.filename)

                    # print(f'{canv.itemcget('image', 'image')=}')
            except Exception as e:
                print(f'error opening image: {str(e)}')

    prep_canvas(canv, startnum)

    display_to_canvas(canv, fpath, startnum)


def prep_canvas(canv, startnum):
    """Prepare the Canvas for image display by creating the list of objects.
    Uses these module variables:
        image_objects
        images_opened
        images_selected
    """
    # delete any existing images
    idlist = canv.find_all()
    for n, item in enumerate(idlist):
        canv.delete(item)

    for n, item in enumerate(image_objects[startnum:]):#, startnum):
        centered_x = viewport['w'] / 2
        centered_y = viewport['h'] / 2

        imid = canv.create_image(centered_x, centered_y, image=item, tag='image', state=tk.HIDDEN)
        fname = images_opened[n].split('/')[-1]
        images_selected.append(fname)


def display_to_canvas_ORIG(canv, pathlist, startnum):
    """Display a list of images to a Canvas, one at a time.

    Uses these module variables:
        image_objects
        run_status
        images_selected
        textvar -- a string variable in the image caption
        delay_time
    """
    for n, item in enumerate(image_objects[startnum:], startnum):
        if run_status is True:
            idlist = canv.find_all()
            canv.itemconfigure(idlist[n], state=tk.NORMAL)
            # try/except not needed because when n==0, idlist[-1] acts on the
            # last item in the list, which isn't needed but does no harm.

            if len(idlist) > 1:
                canv.itemconfigure(idlist[n-1], state=tk.HIDDEN)

            fname = images_selected[n]
            lab = str(n + 1) + ' of ' + str(len(pathlist)) + ': ' + fname
            textvar.set(lab)

            canv.update()
            time.sleep(delay_time)
        else:
            break


def display_to_canvas(canv, pathlist, startnum):
    """Display a list of images to a Canvas, one at a time.

    Uses these module variables:
        image_objects
        run_status
        images_selected
        textvar -- a string variable in the image caption
        delay_time
    """
    # display first image
    idlist = canv.find_all()
    for n, item in enumerate(idlist):
        canv.itemconfigure(item, state=tk.HIDDEN)

    canv.itemconfigure(idlist[startnum], state=tk.NORMAL)
    fname = images_selected[startnum]
    lab = str(startnum + 1) + ' of ' + str(len(pathlist)) + ': ' + fname
    textvar.set(lab)

    canv.update()
    time.sleep(delay_time)

    # display any remaining images
    # TODO: ? can I streamline this loop
    if len(idlist) > 1:
        for n, item in enumerate(image_objects[startnum + 1:], startnum + 1):
            if run_status is True:
                # idlist = canv.find_all()
                canv.itemconfigure(idlist[n], state=tk.NORMAL)
                # try/except not needed because when n==0, idlist[-1] acts on the
                # last item in the list, which isn't needed but does no harm.

                # if len(idlist) > 1:
                canv.itemconfigure(idlist[n-1], state=tk.HIDDEN)

                fname = images_selected[n]
                lab = str(n + 1) + ' of ' + str(len(pathlist)) + ': ' + fname
                textvar.set(lab)

                canv.update()
                time.sleep(delay_time)
            else:
                break


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
    h_offset = 6
    v_offset = 6
    # line_height = 12
    line_height = 18
    fig_offset = line_height * 2
    list_offset = 0

    # print(f'{existing_figs=}')
    # print(f'{line_height=}, {fig_offset=}')

    # if len(lens_image_objects) > 0:
    #     # list_offset = (len(lens_image_objects) * line_height) + fig_offset
    #     # figs = len(existing_figs)
    #     # if len(existing_figs) > 1:
    #     #     figs = (len(existing_figs) - 1)
    #     # else:
    #     #     figs = len(existing_figs)
    #
    #     factor = len(existing_figs) * fig_offset
    #
    #     # print(f'{line_height=}, {figs=}')
    #     # list_offset = (len(lens_image_objects) * (line_height * figs))# + fig_offset
    #     list_offset = (len(lens_image_objects) * line_height) + factor
    #     print(f'    {factor=}, {list_offset=}')
    # if len(lens_image_objects) > 0:

    # factor = (len(existing_figs) - 1) * fig_offset
    factor = len(existing_figs) * fig_offset
    list_offset = (len(lens_image_objects) * line_height) + factor
    # print(f'    {factor=}, {list_offset=}')


    # else:
    #     # zero (first line)
    #     list_offset = len(lens_image_objects)

    # If the figure no longer exists (window was closed), delete its list.
    # This should be done in a function.
    # canv_1.delete('file_list')

    # Display a title for the list
    figures = plt.get_fignums()
    figure_text = 'Figure ' + str(figures[-1])
    # canv_1.create_text(h_offset, v_offset + list_offset, text=figure_text, font=helv12b, anchor='nw', tags='list_title')

    figure_fr = add_text_frame(figure_text)

    for n, item in enumerate(fpath):
        # ? need this
        # if run_status is True:
        try:
            im = Image.open(item)
            images_opened.append(item)
            image_objects.append(im)
        except Exception as e:
            print(f'error opening image: {str(e)}')

        # update spacing for next list, if any
        lens_image_objects.append(len(item))

    display_to_plot(list_offset, figure_fr, 0)


def display_to_plot(list_offset, fr, startnum=0):
    global image_objects
    global images_opened
    global run_status

    h_offset = 6
    v_offset = 6
    line_height = 18

    # has no effect:
    # canv_1.master.focus_set()

    for n, item in enumerate(image_objects[startnum:], startnum):
        # print(f'{n=}, {run_status=}')
        if run_status is True:
            plt.clf()
            # imshow creates the matplotlib Artist "AxesImage" in the container "ax.images"
            plt.imshow(item)
            plt.axis("off")

            filename = images_opened[n].split('/')[-1]
            images_selected.append(filename)

            item_text = str(n + 1) + ': ' + filename
            text_x = h_offset
            text_y = (n * line_height) + line_height + (v_offset * 2) + list_offset
            # canv_1.create_text(text_x, text_y, text=item_text, font=helv12, anchor='nw', tags='file_list')
            add_text(fr, item_text)

            plt.title('image ' + item_text)
            # fig.canvas.toolbar.pack_forget()

            # has no effect:
            canv_1.master.focus_set()
            plt.pause(3)
        else:
            break


def add_text_frame(line: str) -> object:
    text_frame = ttk.Frame(report)
    text_frame.pack(fill='both', expand=True)

    lin = ttk.Label(text_frame, anchor='w', text=line, font=helv12b)
    lin.pack(anchor='w', padx=3, pady=5)

    return text_frame


def add_text(parent: object, line: str) -> None:
    lin = ttk.Label(parent, anchor='w', text=line, font=helv12)#, background='cyan')
    lin.pack(anchor='w', fill='both')


def add_image(canv: object, fpath: tuple | str):
    global display_method

    match display_method:
        case "canvas":
            use_canvas(canv, fpath)
        case "plot":
            use_plot(fpath)


def set_delay(var: tk.StringVar):
    global delay_time

    delay_time = int(var.get())


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
    # print(f'    next: {image_objects[num]} ({images_opened[num]})')

    thisnum = 0
    if display_method == 'canvas':
        # which image is displayed?
        for n, item in enumerate(canv.find_all()):
            if canv.itemcget(item, "state") == "normal":
                thisnum = n + 1
        else:
            pass
        # print(f'{thisnum=}')
        display_to_canvas(canv, tuple(images_opened), thisnum)
    else:
        thisnum = len(images_selected)
        print(f'{thisnum=}')
        display_to_plot(tuple(images_opened), thisnum)


def step_forward():
    if run_status == False:
        # display the next image in the current show list
        if display_method == 'canvas':
            pass
        else:
            pass


def step_back():
    if run_status == False:
        # display the previous image in current show list
        if display_method == 'canvas':
            pass
        else:
            pass


def get_list_display():
    pass


def on_close(ev):
    # print(f'in on_close, {ev=}')
    # ev.canvas.figure.number
    pass



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
canv_1.bind('<Configure>', lambda ev,
                                  vp=viewport: cnv_ui.resize_viewport(ev, vp))
canv_1.master.bind('<Control-Down>',
                   lambda ev: pause_show(ev)
                   )
canv_1.master.bind('<Control-Up>',
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

open_button = ttk.Button(root, text="Open Files", command=lambda c=canv_1: select_image_file(c))
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
