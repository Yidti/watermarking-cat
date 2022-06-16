import tkinter.font
import tkinter.messagebox
from tkinter import *
from PIL import ImageTk, Image, ImageDraw, ImageFont
from tkinter.filedialog import askopenfilenames, askdirectory
import os

_theme_color_1 = 'Light Blue'
_theme_color_2 = 'Sky Blue'
_theme_color_3 = 'Light Steel Blue'
_theme_color_4 = 'Steel Blue'
_theme_color_5 = 'Dodger Blue'

# save path of files
filepaths, filepaths_2d = None, None
#
images_2d_edit = None
# save resized images
photo_thumbnails_2d = None
button_thumbnails_2d = None
# save original images
images_2d_show = None
# edit image
img_show, img_open, img_resize, img_watermark = None, None, None, None
img_path = None
img_resize_opacity = None
img_location = None


class CustomButton(Button):
    def __init__(self, *args, **kwargs):
        Button.__init__(self, *args, **kwargs)
        self['highlightthickness'] = 2
        self['relief'] = FLAT
        self['borderwidth'] = 0
        self['highlightbackground'] = _theme_color_3
        self['font'] = ("Arial", 25)


def convert_1d_to_2d(list_1d, cols) -> list:
    return [list_1d[i:i + cols] for i in range(0, len(list_1d), cols)]


def get_display_size():
    root = Tk()
    root.update_idletasks()
    height = root.winfo_screenheight()
    width = root.winfo_screenwidth()
    root.destroy()
    return width, height


def _get_photo_thumbnail():
    global filepaths, filepaths_2d
    expected_width = 255
    image_open = [Image.open(filepath) for filepath in filepaths]
    image_size = [(image.width, image.height) for image in image_open]
    image_thumbnail = []
    for index, image in enumerate(image_open):
        scale_for_height = expected_width / image_size[index][0]
        image_thumbnail.append(
            image.resize((expected_width, int(scale_for_height * image_size[index][1])), Image.ANTIALIAS))

    photo_thumbnail = [ImageTk.PhotoImage(image) for image in image_thumbnail]

    return photo_thumbnail


class WatermarkingCat(Tk):
    def __init__(self):
        super().__init__()
        self.image_top_level = None
        self.watermarking_top_level = None
        self._select_button: Button = None
        self._clear_button: Button = None
        self._export_button: Button = None
        self._canvas: Canvas = None
        self.buttons_frame = None
        self._button_thumbnails: list = []
        self.arial_font_image = None
        self.arial_font_widget = None
        self._export_directory = None
        self._watermark_content = '''Copyright © watermarking cat \n Created by Sola \n Welcome to contact me'''
        self._screen = get_display_size()
        self.initial_ui()

    def initial_ui(self: Tk):
        self.title("Watermarking Cat")
        self.config(background=_theme_color_1, pady=10)
        center_x = self._screen[0] // 2 - 800 // 2
        center_y = self._screen[1] // 2 - 600 // 2
        self.geometry('{}x{}+{}+{}'.format(800, 600, center_x, center_y))
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # background frame
        background_frame = Frame(self, bg=_theme_color_2, pady=10, bd=1, relief=FLAT)
        background_frame.grid(row=0, column=0, sticky=NSEW)
        background_frame.rowconfigure(0, weight=1)
        background_frame.rowconfigure(1, weight=20)
        background_frame.columnconfigure(0, weight=1)
        # first row put control frame
        control_frame = Frame(background_frame, bg=_theme_color_3, bd=1, relief=FLAT, padx=20)
        control_frame.grid(row=0, column=0, sticky=NSEW, pady=10)
        control_frame.rowconfigure(0, weight=1)
        control_frame.columnconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        # control_frame.columnconfigure(2, weight=1)
        self._select_button = CustomButton(control_frame, text="Select", command=self._thumbnails)
        self._select_button.grid(row=0, column=0, sticky=NSEW)
        self._clear_button = CustomButton(control_frame, text="Clear", command=self._clear, state='disabled')
        self._clear_button.grid(row=0, column=1, sticky=NSEW)
        # self._export_button = CustomButton(control_frame, text="Export", command=self._export, state='disabled')
        # self._export_button.grid(row=0, column=2, sticky=NSEW)
        # second row put picture frame for the canvas and scrollbar
        picture_frame = Frame(background_frame, bg=_theme_color_4, bd=0, pady=5, relief=FLAT)
        picture_frame.grid(row=1, column=0, sticky=NSEW)
        picture_frame.rowconfigure(0, weight=1)
        picture_frame.columnconfigure(0, weight=1)
        # Add a canvas in picture frame.
        self._canvas = Canvas(picture_frame, bg=_theme_color_5, bd=0, highlightthickness=0)
        self._canvas.grid(row=0, column=0, sticky=NSEW)
        # Create a vertical scrollbar linked to the canvas.
        vs_bar = Scrollbar(picture_frame, orient=VERTICAL, command=self._canvas.yview)
        vs_bar.grid(row=0, column=1, sticky=NS)
        self._canvas.configure(yscrollcommand=vs_bar.set)
        # setup font
        self.arial_font_image = ImageFont.truetype("Arial Unicode MS.ttf", 60)

    def _thumbnails(self):
        global filepaths, filepaths_2d
        global photo_thumbnails_2d
        global button_thumbnails_2d
        global images_2d_show, images_2d_edit

        # choose multiple pictures
        f_types = [('JPG Files', '*.jpg'), ('JPEG Files', '*.jpeg'), ('PNG Files', '*.png')]
        filepaths = askopenfilenames(filetypes=f_types, title="Please choose your images")
        if len(filepaths) > 0:

            # image_edit = [Image.open(filename) for filename in filepaths]
            # images_photo = [ImageTk.PhotoImage(image) for image in image_edit]
            # images_2d_edit = convert_1d_to_2d(image_edit, COLS)
            # images_2d_show = convert_1d_to_2d(images_photo, COLS)
            # thumbnails_2d_show = convert_1d_to_2d(thumbnails_photo, COLS)

            # set columns number
            cols = 3
            # convert to 2d
            filepaths_2d = convert_1d_to_2d(filepaths, cols)
            photo_thumbnails_2d = convert_1d_to_2d(_get_photo_thumbnail(), cols)

            # Create a frame on the canvas to contain the grid of buttons.
            self.buttons_frame = Frame(self._canvas)

            # check rows numbers
            rows = len(photo_thumbnails_2d)

            for i in range(0, rows):
                for j in range(0, len(photo_thumbnails_2d[i])):
                    button = CustomButton(self.buttons_frame, padx=7, pady=7, relief=RIDGE,
                                          activebackground='orange', text='(%d,%d)' % (i, j),
                                          image=photo_thumbnails_2d[i][j], compound=TOP,
                                          command=lambda i=i, j=j: self._popup_image(i, j))
                    button.grid(row=i, column=j, sticky='news')
                    self._button_thumbnails.append(button)
            # convert to 2d
            button_thumbnails_2d = convert_1d_to_2d(self._button_thumbnails, cols)

            # Create canvas window to hold the buttons_frame.
            self._canvas.create_window((0, 0), window=self.buttons_frame, anchor=NW)

            self.buttons_frame.update_idletasks()  # Needed to make bbox info available.
            bbox = self._canvas.bbox(ALL)  # Get bounding box of canvas with Buttons.
            self._canvas.configure(scrollregion=bbox)

            self._clear_button['state'] = 'normal'
            # self._export_button['state'] = 'normal'
            self._select_button['state'] = 'disabled'

    def _popup_image(self, i, j):
        global filepaths_2d, img_path, img_location
        global img_show, img_open, img_resize
        global img_watermark

        self._popup_edit_watermark()

        if self.image_top_level is not None:
            self.image_top_level.destroy()
        self.image_top_level = Toplevel()
        self.image_top_level.title(f"image ({i},{j})")
        img_path = filepaths_2d[i][j]
        img_location = (i, j)
        img_open = Image.open(img_path)
        # scale original image fit to screen
        aspect_ratio_screen = self._screen[0] / self._screen[1]
        aspect_ratio_image = img_open.width / img_open.height

        if aspect_ratio_image > aspect_ratio_screen:
            scale = self._screen[0] / (img_open.width * 1.2)
        else:
            scale = self._screen[1] / (img_open.height * 1.2)

        new_size = (int(img_open.width * scale), int(img_open.height * scale))

        img_resize = img_open.resize(new_size, Image.ANTIALIAS)
        img_show = ImageTk.PhotoImage(img_resize)
        img_watermark = Button(self.image_top_level, image=img_show, command=self._popup_edit_watermark)
        img_watermark.pack(fill=BOTH)

    def _popup_edit_watermark(self):
        global img_watermark
        global img_show, img_resize, img_open

        if self.watermarking_top_level is not None:
            self.watermarking_top_level.destroy()
        self.watermarking_top_level = Toplevel(self.image_top_level)
        self.watermarking_top_level.title("Edit your Watermark")
        top_width = 600
        top_height = 200
        padding_x = 100
        position_x = self._screen[0] - top_width - padding_x
        position_y = self._screen[1] // 2 - top_height // 2
        self.watermarking_top_level.geometry('{}x{}+{}+{}'.format(top_width, top_height, position_x, position_y))

        self._watermark_content = '''Copyright © watermarking cat \n Created by Sola \n Welcome to contact me'''

        Label(self.watermarking_top_level, text="Add Text").pack()

        font_local = tkinter.font.Font(size=30)
        text = Text(self.watermarking_top_level, padx=10, pady=10, height=3, font=font_local)
        text.tag_configure("center", justify='center')
        text.tag_add("center", 1.0, "end")
        text.insert(END, self._watermark_content, "center")
        text.pack()
        spinbox_value = IntVar()
        spinbox_value.set("60")
        Label(self.watermarking_top_level, text="Scale").pack(side=LEFT, padx=10)
        spin_box = Spinbox(self.watermarking_top_level, width=5, from_=30, to=100, increment=5,
                           textvariable=spinbox_value,
                           wrap=True)
        spin_box.pack(side=LEFT)
        Button(self.watermarking_top_level, text="Apply",
               command=lambda: self.add_watermark(text=text, font_size=spin_box)).pack(side=LEFT,
                                                                                       padx=10)
        Button(self.watermarking_top_level, text="Save",
               command=self._save).pack(side=LEFT)
        # self.watermarking_top_level.attributes('-topmost', 'true')
        self.watermarking_top_level.lift(self.image_top_level)

    def add_watermark(self, text, font_size):
        global img_resize, img_show, img_resize_opacity
        global img_watermark, photo_thumbnails_2d
        global button_thumbnails_2d
        global img_location
        lines_list = text.get("1.0", END).splitlines()
        self._watermark_content = "\n".join([line.strip() for line in lines_list])

        # make a blank image for the text, initialized to transparent text color
        img_text_opacity = Image.new('RGBA', img_resize.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img_text_opacity)
        arial_font = ImageFont.truetype("Arial Unicode MS.ttf", int(font_size.get()))

        content = self._watermark_content
        w, h = draw.multiline_textsize(content, font=arial_font)
        draw.multiline_text(((img_resize.width - w) / 2, (img_resize.height - h) / 2), content, (0, 0, 255, 70),
                            font=arial_font, align="center")
        if img_resize.mode == "RGB":
            img_resize = img_resize.convert("RGBA")
        # img_text_opacity
        img_resize_opacity = Image.alpha_composite(img_resize, img_text_opacity)
        # update watermark
        img_show = ImageTk.PhotoImage(img_resize_opacity)
        img_watermark.configure(image=img_show)

        # check thumbnails
        button_thumbnails_2d[img_location[0]][img_location[1]]['text'] = "✓"

    def _save(self):
        global img_watermark, img_path, img_resize_opacity
        image = img_resize_opacity

        directory = askdirectory(initialdir="/", title="Select Your Export Directory")
        if directory != "":
            self._export_directory = directory + "/output"
            os.makedirs(self._export_directory, exist_ok=True)

            if img_watermark is not None:
                if image.mode == "RGB":
                    image = img_resize_opacity.convert("RGBA")

                # export watermark
                filename = os.path.split(img_path)[1]
                filepath, file_extension = os.path.splitext(img_path)
                if file_extension == ".jpg" or file_extension == ".jpeg":
                    image = image.convert(mode="RGB")
                export = self._export_directory + "/" + filename
                image.save(export)

    """
    def _export(self):
        global img_resize, img_show, images_2d_show, filepaths_2d, images_2d_edit

        directory = askdirectory(initialdir="/", title="Select Your Export Directory")
        if directory != "":
            self._export_directory = directory + "/output"
            os.makedirs(self._export_directory, exist_ok=True)

            rows = len(images_2d_edit)
            for i in range(0, rows):
                for j in range(0, len(images_2d_edit[i])):
                    export_image = images_2d_edit[i][j]
                    path = filepaths_2d[i][j]
                    self._save_image(export_image, path)
            tkinter.messagebox.showinfo("Export Directory", "Successfully!")
    """

    """
    def _save_image(self, image, path):
        # make a blank image for the text, initialized to transparent text color
        font_size = 60
        content = self._watermark_content
        img_text_opacity = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img_text_opacity)
        arial_font = ImageFont.truetype("Arial Unicode MS.ttf", font_size)

        w, h = draw.multiline_textsize(content, font=arial_font)
        draw.multiline_text(((image.width - w) / 2, (image.height - h) / 2), content, (0, 0, 255, 70),
                            font=arial_font, align="center")
        if image.mode == "RGB":
            image = image.convert("RGBA")
        # img_text_opacity
        img_opacity = Image.alpha_composite(image, img_text_opacity)
        # export watermark
        filename = os.path.split(path)[1]

        filepath, file_extension = os.path.splitext(path)
        if file_extension == ".jpg" or file_extension == ".jpeg":
            img_opacity = img_opacity.convert(mode="RGB")
        export = self._export_directory + "/" + filename
        img_opacity.save(export)
    """

    def _clear(self):

        if self.image_top_level is not None:
            self.image_top_level.destroy()

        if self.watermarking_top_level is not None:
            self.watermarking_top_level.destroy()

        self._clear_button['state'] = 'disabled'
        # self._export_button['state'] = 'disabled'
        self._select_button['state'] = 'normal'

        self._export_directory = None
        global filepaths_2d, photo_thumbnails_2d, images_2d_show
        filepaths_2d = None
        photo_thumbnails_2d = None
        images_2d_show = None
        self._canvas.update_idletasks()
        self._canvas.delete("all")
        print('clear')

    def run(self):
        self.mainloop()
