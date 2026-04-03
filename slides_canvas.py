"""
program: slides_canvas.py

purpose: For project slideshow.

comments: Demonstrates the display of one or more images in succession,
          using the Canvas object.

          No Artificial Intelligence was used in production of this code.

author: Russell Folks

history:
-------
12-10-2025  extracted from the original main file that used a flag to run
            either this method or the matplotlib method of image display
03-26-2026  Split into two applications, based on the display method:
            slides_canvas and slides_plot. Remove window reset option. Remove
            some old code, comments and debug statements.
04-01-2026  Add restart current slideshow from the beginning.
"""
import tkinter as tk
from tkinter import ttk, filedialog
from importlib.machinery import SourceFileLoader
import time
import tkinter.font as tkfont

from ttkthemes import ThemedTk
from PIL import Image, ImageTk

sttk = SourceFileLoader("styles_ttk", "../styles/styles_ttk.py").load_module()
cnv_ui = SourceFileLoader("cnv", "../canvas/canvas_ui.py").load_module()
sel = SourceFileLoader("ui", "../utilities/tool_classes.py").load_module()

root = ThemedTk()
root.resizable(True, True)
root.title("canvas, ttk, pack")

delay_time = 3

helv12 = tkfont.Font(family='Helvetica', size=12)
helv12b = tkfont.Font(family='Helvetica', size=12, weight='bold')

# test
canv_config_flag = False
enter_win_flag = False
leave_win_flag = False
# END test

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
        # twindow_reset doesn't exist anymore, but do we need to do a focus_set?
        # window_reset.focus_set()


def use_canvas(canv: object,
               fpath: tuple | str,
               startnum: int=0
               ) -> None:
    """Create a PIL PhotoImage for each file in a list of paths.

    Uses module variables:
        im_tk
        image_objects
        images_opened

    Calls:
        prep_canvas
        display_to_canvas
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
            except Exception as e:
                print(f'error opening image: {str(e)}')

    prep_canvas(canv, startnum)

    display_to_canvas(canv, fpath, startnum)


def prep_canvas(canv: object, startnum: int) -> None:
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


def display_to_canvas(canv: object,
                      pathlist: list,
                      startnum: int
                      ) -> None:
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
    # TODO: ? streamline this loop
    if len(idlist) > 1:
        for n, item in enumerate(image_objects[startnum + 1:], startnum + 1):
            if run_status is True:
                # idlist = canv.find_all()
                canv.itemconfigure(idlist[n], state=tk.NORMAL)
                canv.itemconfigure(idlist[n-1], state=tk.HIDDEN)

                fname = images_selected[n]
                lab = str(n + 1) + ' of ' + str(len(pathlist)) + ': ' + fname
                textvar.set(lab)

                canv.update()
                time.sleep(delay_time)
            else:
                break


# def add_text(container: object,
#              line: str,
#              xy: tuple) -> None:
#     container.create_text(xy[0], xy[1], anchor='w', font='helv12', text=line)
#     container.configure(scrollregion=container.bbox("all"))


def add_image(canv: object, fpath: tuple | str) -> None:
    use_canvas(canv, fpath)


def set_delay(var: tk.StringVar) -> None:
    global delay_time

    delay_time = int(var.get())


def pause_show(ev):
    """Temporarily halt the sequential display of images.

    uses module level objects:
    images_opened, image_objects
    """
    global run_status

    run_status = False
    # print(f'in pause_show')
    # print(f'    images shown: {len(images_selected)}, last: {images_selected[-1]}')

    # files = [i.split('/')[-1] for i in images_opened]
    # print(f'    {files=}')
    # print(f'    {len(image_objects)=}')


def resume_show(ev, canv: object) -> None:
    global images_opened
    global images_selected
    global run_status

    run_status = True
    print(f'in resume_show')
    # print(f'    next: {image_objects[num]} ({images_opened[num]})')

    thisnum = 0
    # which image is displayed?
    for n, item in enumerate(canv.find_all()):
        if canv.itemcget(item, "state") == "normal":
            thisnum = n + 1
            break    # only one is normal

    # TODO: thisnum won't work if the show was paused on the last image (there is no n + 1)
    #       We need extra variables for slide numbers (total, current, etc.)
    display_to_canvas(canv, tuple(images_opened), thisnum)


# def restart_slides(ev, canv: object) -> None:
def restart_slides(canv: object) -> None:
    global images_opened
    global images_selected
    global run_status

    run_status = True
    thisnum = 0
    display_to_canvas(canv, tuple(images_opened), thisnum)


def step_forward():
    """Display the next image in the current show list"""
    # if run_status:
    if run_status == False:
        pass


def step_back():
    """Display the previous image in current show list."""
    # if run_status:
    if run_status == False:
        pass


# not needed?
# def on_close(ev):
#     # print(f'in on_close, {ev=}')
#     # ev.canvas.figure.number
#     pass


# works with the canvas, but should it be viewport
# ? what can we do with this. It may have been an attempt to pause the show.
def read_but1(ev, vp):
    print(f'in read_but1... {ev}')

    # ? what does this do
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
            break  # there should be only one 'normal'

    # try
    im = Image.open(images_opened[-1])
    params = cnv_ui.calc_resize_to_vp(viewport, im)
    canv.configure(width=params['wid_int'], height=params['ht_int'])
    canv.update()
    # END try

    # use_canvas(canv, tuple(images_opened), thisnum)


def set_enter_win():
    enter_win_flag = True
    print(f'in set_enter_win:\n    {canv_config_flag=}, {enter_win_flag=}, {leave_win_flag=}')


def set_leave_win():
    leave_win_flag = True
    print(f'in set_leave_win:\n    {canv_config_flag=}, {enter_win_flag=}, {leave_win_flag=}')


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
                                  vp=viewport,
                                  f=canv_config_flag: cnv_ui.resize_viewport(ev, vp, f))

canv_1.bind('<Button-1>', lambda ev, vp=viewport: read_but1(ev, vp))

# test
canv_1.bind('Enter', set_enter_win)
canv_1.bind('Leave', set_leave_win)
# END test

canv_1.master.bind('<Control-Down>',
                   lambda ev: pause_show(ev)
                   )
canv_1.master.bind('<Control-Up>',
                   lambda ev,
                          canv=canv_1: resume_show(ev, canv)
                   )

report = ttk.Frame(root)
report.pack(fill='both', expand=True)

textvar = tk.StringVar()
caption = ttk.Entry(root, justify='center', textvariable=textvar)
caption.pack(fill='x', expand=True)
caption.update()

open_button = ttk.Button(root, text="Open Files", command=lambda c=canv_1: select_image_file(c))
open_button.pack(pady=my_pady)

ui_fr = ttk.Frame(root, style='basic.TFrame')

delay = tk.StringVar(value='3')
enter_delay_time = sel.EntryFrame(ui_fr,
                                  display_name='Delay',
                                  name='delay',
                                  posn=[0],
                                  stick='w',
                                  var=delay,
                                  callb=lambda var=delay: set_delay(var)
                                  )

restart_show = ttk.Button(ui_fr, text="restart slides",
                          command=lambda canv=canv_1: restart_slides(canv),
                          style="MyButton1.TButton")
restart_show.pack(ipadx=5, ipady=0, padx=5, pady=5)

ui_fr.pack(padx=5, pady=5)
# ui_fr.update()

btnq = ttk.Button(root,
                  text="Quit",
                  command=root.quit,
                  style="MyButton1.TButton")
btnq.pack(side="top", pady=my_pady)
btnq.update()

# show some layout dimensions
# ----
print(f'canv_1 h,w: {canv_1.winfo_height()}, {canv_1.winfo_width()}')
print(f'ui_fr h,w: {ui_fr.winfo_height()}, {ui_fr.winfo_width()}')

# update widget sizes
print(f'{root.geometry()=}')
total_ht = canv_1.winfo_height() + caption.winfo_height() + open_button.winfo_height() + ui_fr.winfo_height() + btnq.winfo_height()
total_wd = max(canv_1.winfo_width(), ui_fr.winfo_width())
print(f'{total_ht=}, {total_wd=}')

# default_dims = f'{total_wd}x{total_ht}'
default_dims = root.geometry()

# root.minsize(total_wd, total_ht)
root.minsize(400, 474)
print(f'{root.geometry()=}')

if __name__ == "__main__":
    root.mainloop()
