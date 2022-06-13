from tkinter import Tk, Text, filedialog, Canvas, BOTH, W, N, E, S
from tkinter.filedialog import askopenfile
from tkinter.ttk import Frame, Button, Label, Style, LabelFrame
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk
import cv2
import numpy as np

class App(Frame):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        self.master.title("Windows")
        self.pack(fill=BOTH, expand=True)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        lblf_select = LabelFrame(self, text='Select File')
        lblf_select.grid(column=0, row=0, padx=20, pady=20, sticky="nw")

        btn_select = Button(lblf_select, text="Select")
        btn_select['command'] = self.action_btn_select
        btn_select.grid(column=0, row=0, padx=5, pady=5)

        lblf_process = LabelFrame(self, text='Options')
        lblf_process.grid(column=1, row=0, padx=20, pady=20, sticky="ne")

        btn_process = Button(lblf_process, text="Process")
        btn_process['command'] = self.action_btn_process
        btn_process.grid(column=1, row=0, padx=5, pady=5)

        lblf_original = LabelFrame(self, text='Original Image')
        lblf_original.grid(column=0, row=1, padx=10, pady=10)

        self.cvs_original = Canvas(lblf_original, width=400, height=400, bg='green') 
        self.cvs_original.grid(padx=10, pady=10)

        lblf_processed = LabelFrame(self, text='Processed Image')
        lblf_processed.grid(column=1, row=1, padx=10, pady=10)

        self.cvs_processed = Canvas(lblf_processed, width=400, height=400, bg='red') 
        self.cvs_processed.grid(padx=10, pady=10)

    def action_btn_select(self):
        global filename
        f_types = [('Png Files', '*.png')]
        filename = filedialog.askopenfilename(filetypes=f_types)

        image = cv2.imread(filename)

        blue,green,red = cv2.split(image)
        img = cv2.merge((red,green,blue))
        im = Image.fromarray(img)
        image_resize = im.resize((402, 402))
        self.img = ImageTk.PhotoImage(image=image_resize)
        self.cvs_original.create_image(0,0, anchor='nw', image=self.img)    
        self.cvs_original.image = self.img

    def action_btn_process(self):

        # Load image, grayscale, median blur, sharpen image
        image = cv2.imread(filename)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.medianBlur(gray, 5)
        sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpen = cv2.filter2D(blur, -1, sharpen_kernel)

        # Threshold and morph close
        thresh = cv2.threshold(sharpen, 160, 255, cv2.THRESH_BINARY_INV)[1]
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

        contours, hierarchy = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        img_contours = np.zeros(image.shape)
        cv2.drawContours(img_contours, contours, -1, (0,255,0), 1)

        min_area = 100
        max_area = 1500
        image_number = 0
        for c in contours:
            area = cv2.contourArea(c)
            if area > min_area and area < max_area or True:
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 2)
                image_number += 1

        #Rearrange colors
        blue,green,red = cv2.split(image)
        img = cv2.merge((red,green,blue))
        im = Image.fromarray(img)
        image_resize = im.resize((402, 402))
        self.imgtk = ImageTk.PhotoImage(image=image_resize)
        
        self.cvs_processed.create_image(0,0, anchor='nw', image=self.imgtk)    
        self.cvs_processed.image = self.imgtk

def main():

    root = Tk()
    root.geometry("1040x580+300+300")
    root.resizable(0, 0)
    app = App()
    root.mainloop()


if __name__ == '__main__':
    main()