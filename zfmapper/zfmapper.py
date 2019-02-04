#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""
   Copyright 2018 Dai Yamamoto
   Copyright 2018-2019 Daisuke Sato

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


import tkinter as tk
from tkinter import filedialog as tkFileDialog
from tkinter import scrolledtext as ScrolledText
from tkinter import messagebox
import os
import sys
import numpy as np
import pandas as pd
from tifffile import imread
import re

VERSION = "0.1.0"


class ZFMapperFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.create_widgets()
        self.target_files = ()

    def create_widgets(self):
        self.lbl1 = tk.Label(self, text="ZF-Mapper v" + VERSION)
        self.lbl1.pack()
        """
        threshold color setting UI
        """
        th_color_frame = tk.Frame(self)
        th_color_frame.pack()
        lbl2 = tk.Label(th_color_frame, text="threshold color: ")
        lbl2.pack(side=tk.LEFT)
        self.th_color = tk.IntVar()
        self.th_color.set(1)
        rad1 = tk.Radiobutton(th_color_frame, text="Red", value=1, variable=self.th_color)
        rad1.pack(side=tk.LEFT)
        rad2 = tk.Radiobutton(th_color_frame, text="Green", value=2, variable=self.th_color)
        rad2.pack(side=tk.LEFT)

        """
        threshold value setting UI
        """
        th_value_frame = tk.Frame(self)
        th_value_frame.pack()
        lbl3 = tk.Label(th_value_frame, text="threshold value: ")
        lbl3.pack(side=tk.LEFT)
        self.txt1 = tk.Entry(th_value_frame, width=10)
        self.txt1.insert(tk.END, "10")
        self.txt1.pack(side=tk.LEFT)

        """
        file select UI
        """
        btn1 = tk.Button(self, text="Select File(s)", command=self.load_files)
        btn1.pack()
        lbl_filelist = tk.Label(self, text="Selected File(s):")
        lbl_filelist.pack()
        self.txt_filelist = ScrolledText.ScrolledText(self, width=100, height=10)
        self.txt_filelist.insert(tk.INSERT, "No Files Selected")
        self.txt_filelist.pack()

        """
        process UI
        """
        btn2 = tk.Button(self, text="Process File(s)", command=self.process_files)
        btn2.pack()

        self.process_status = tk.Label(root, text="Ready.", borderwidth=2, relief="groove")
        self.process_status.pack(side=tk.BOTTOM, fill=tk.X)

    def showinfo(self):
        msg = "ZF-Mapper Ver."+VERSION+"\n\nGitHub: https://github.com/YShimada0419/ZF-Mapper"
        tk.messagebox.showinfo("About", msg)

    def load_files(self):
        self.target_files = tkFileDialog.askopenfilenames(parent=root, title='Choose a file')
        file_list = ""
        for f in self.target_files:
            if not len(file_list) == 0:
                file_list += "\n"
            file_list += f
        self.txt_filelist.delete(1.0, tk.END)
        self.txt_filelist.insert(tk.INSERT, file_list)
        self.process_status["text"] = str(len(self.target_files)) + " files selected."

    def process_files(self):
        files = self.target_files
        th = int(self.txt1.get())
        print(self.target_files)
        if self.th_color.get() == 1:
            print("RED " + str(th))
            target_color="red"
        if self.th_color.get() == 2:
            print("GREEN " + str(th))
            target_color="green"
        self.process_status["text"] = "Processing, color: " + target_color + " th: " + str(th)
        process_image(args=files, color=target_color, threshold=th)
        self.process_status["text"] = "Finished processing, color: " + target_color + " th: " + str(th)


def process_image(args, color="red", threshold=0):
    for arg in args:
        print('arg:%s' % arg)
        fname = arg.split('/')[-1]
        path = arg[:(-1 * len(fname))]
        dname = path
        output_dir = path
        fname_without_extention, filetype = os.path.splitext(fname)
        fname_without_suffix = re.sub(r'^[rg]_', '', fname_without_extention)
        print('filename:%s' % fname)
        print('path:%s' % path)
        print('filetype:%s' % filetype)

        if sys.platform.startswith('darwin') and path.find('Contents/MacOS') >= 0:
            with open('/tmp/zfmapper_log.txt', 'w') as f:
                f.write('configdir:'+str(dname)+'/../../../\r\n'+'args:'+str(args))
        elif fname[0] == '.':
            pass
        else:
            print('Processing %s' % fname)

            target_color = color
            threshold = threshold

            # load image file
            print('%s%s' % (dname, fname))
            img_tiff = imread('%s%s' % (dname, fname))

            # translate to 8bit image
            if(img_tiff.dtype != 'uint8'):
                print('converting to uint8')
                img_tiff = (img_tiff/256).astype('uint8')

            # initialize result array
            data = {
                'x': [],
                'y': [],
                'r': [],
                'g': [],
                'b': [],
            }

            # load pixel info
            pix = img_tiff.ravel()
            rs = pix[0::3]
            gs = pix[1::3]
            bs = pix[2::3]

            l = rs.shape[0]

            if target_color == 'green':
                valid_pix = np.array(range(l))[gs > threshold]
            if target_color == 'red':
                valid_pix = np.array(range(l))[rs > threshold]

            data['y'] = valid_pix//img_tiff.shape[1]
            data['x'] = valid_pix % img_tiff.shape[1]
            data['r'] = rs[valid_pix]
            data['g'] = gs[valid_pix]
            data['b'] = bs[valid_pix]

            if not len(data['x']) == 0:
                xmin_tiff = data['x'].min()
            else:
                data['x'] = np.ndarray([0])
                xmin_tiff = np.int32(0)
            if not len(data['y']) == 0:
                ymin_tiff = data['y'][data['x'] == xmin_tiff].min()
            else:
                data['y'] = np.ndarray([0])
                ymin_tiff = np.int32(0)

            # normalization
            data['x'] = data['x'] - xmin_tiff
            data['y'] = (data['y'] - ymin_tiff)
            if target_color == 'red':
                data['y'] = data['y'] * -1

            # framing
            df_tiff = pd.DataFrame(data=data)

            # export as csv
            df_tiff[['x', 'y', target_color[:1]]].to_csv('%s/%s_%s_th%s.csv' % (output_dir, fname_without_suffix, target_color, threshold), index=False, sep=',')
            print("done")


if __name__ == '__main__':
    root = tk.Tk()
    root.title("ZF-Mapper")
    root.geometry('400x350')
    menubar = tk.Menu(root)

    app = ZFMapperFrame(master=root)

    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open", command=app.load_files)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label="About", command=app.showinfo)
    menubar.add_cascade(label="Help", menu=helpmenu)
    root.config(menu=menubar)

    """
    main
    """
    root.mainloop()
