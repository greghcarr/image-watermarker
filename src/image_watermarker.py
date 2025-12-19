from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageFont, ImageDraw
from PIL.ImageMath import imagemath_equal, imagemath_int, imagemath_max, imagemath_min
from pathlib import Path


class ImageWatermarker(Tk):
    def __init__(self):
        super().__init__()
        self.title('Image Watermarker')

        frm = ttk.Frame(self, padding=10)
        frm.grid()

        # ttk.Label(frm, text="Image Watermarker").grid(row=0, column=0)
        
        # self.image_path = 'resources/1x1.png'
        # self.image_original = Image.open(self.image_path).convert('RGBA')
        self.image_original = Image.new('RGBA', (1, 1), color=(0, 0, 0, 0))
        self.image_resized = (self.image_original
                                  .resize((int(self.winfo_screenwidth() / 8), 
                                          int(self.winfo_screenheight() / 8)),
                                          Image.Resampling.LANCZOS))
        self.image_resized_ref = ImageTk.PhotoImage(self.image_resized)
        self.image_label = ttk.Label(frm, image=self.image_resized_ref)
        self.image_label.grid(row=1, column=0)
        
        ttk.Button(frm, text="Open Image", command=self.choose_image).grid(row=2, column=0)
        
        self.watermark_text = StringVar()
        self.watermark_text_box = ttk.Entry(frm, justify=CENTER, textvariable=self.watermark_text, width = 20)
        self.watermark_text_box.insert(0, 'Watermark Text')
        self.watermark_text_box.grid(row=3, column=0)
        
        self.button_watermark = ttk.Button(frm, 
                                           text="Watermark It! (disabled)", 
                                           command=(lambda: self.watermark_image(text=self.watermark_text_box.get())), 
                                           state=DISABLED)
        self.button_watermark.grid(row=4, column=0)
        
        ttk.Button(frm, text="Quit", command=self.destroy).grid(row=5, column=0)

        self.mainloop()

    def choose_image(self):
        self.image_path = filedialog.askopenfilename(
            title="Select the image to watermark",
            initialdir="/",  # Start in the root directory (adjust as needed)
            filetypes=(
                ("Image Files", ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.tiff"]),
                ("All Files", "*.*")
            )
        )
        # open the image from the chosen path
        self.image_original = Image.open(self.image_path).convert('RGBA')
        
        # create a copy that is half the height of the screen to display in the window
        new_size = (
            int((self.image_original.size[0] / self.image_original.size[1]) * (self.winfo_screenheight() / 2)),
            int(self.winfo_screenheight() / 2))
        image_resized_display = self.image_original.resize(new_size, Image.Resampling.LANCZOS)
        self.image_resized_ref = ImageTk.PhotoImage(image_resized_display)
        self.image_label.config(image=self.image_resized_ref)
        
        # enable the watermark button
        self.button_watermark.config(text='Watermark It!', state=NORMAL)
        return
    
    def watermark_image(self, text = 'Kohm Gahn'):
        text_image = Image.new('RGBA', self.image_original.size, (255, 255, 255, 0))
        font_size = max((10, ((self.image_original.size[0] + self.image_original.size[1]) /2) //30))
        font = ImageFont.load_default(size=font_size)
        
        d = ImageDraw.Draw(text_image)
        text_color = (20, 20, 20, 200) if sum(self.image_original.getpixel((0,0))) > ((255*3)/2) else (255, 255, 255, 200)
        d.text((0, 0), text, font=font, fill=text_color)
        
        image_watermarked = Image.alpha_composite(self.image_original, text_image)
        image_watermarked = image_watermarked.convert('RGB')
        
        p = Path(self.image_path)
        watermarked_image_path = p.with_stem(f'{p.stem}_watermarked')
        try:
            image_watermarked.save(watermarked_image_path)
        except PermissionError as e:
            messagebox.showerror(f"Error: Permission denied when writing to the file. Details: {e}")
        except FileNotFoundError as e:
            messagebox.showerror(f"Error: The directory for the file does not exist. Details: {e}")
        except OSError as e:
            # Catches other OS errors like 'disk full'
            messagebox.showerror(f'Error: An OS error occurred during file writing. Details: {e}')
        except Exception as e:
            messagebox.showerror(f"Error: An unexpected exception occurred. Details: {e}")
        else:
            messagebox.showinfo('Success!', 'Watermarked image saved to:\n' + watermarked_image_path.__str__() + '.')
