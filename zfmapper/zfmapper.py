#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from __future__ import print_funtcion
import os
import sys
import numpy as np
import pandas as pd
from tifffile import imread
import configparser
import re

VERSION='0.0.3'

args = sys.argv


class Settings:
    def __init__(self, args):
        self.delimiter = '\\' if os.name == 'nt' else '/'
        self.args = args

    def parse_config(self, directory_name):
        inifile = configparser.ConfigParser()
        try:
            inifile.read('%sconfig.ini' % directory_name, 'utf-8')
            self.g_threshold = int(inifile.get('green', 'threshold'))
            self.r_threshold = int(inifile.get('red', 'threshold'))
        except configparser.NoSectionError:
            initial_config = '[red]\r\nthreshold = 3\r\n\r\n[green]\r\nthreshold = 50\r\n'
            with open('%sconfig.ini' % directory_name, 'w') as f:
                f.write(initial_config)
            inifile.read('%sconfig.ini' % directory_name, 'utf-8')
            self.g_threshold = int(inifile.get('green', 'threshold'))
            self.r_threshold = int(inifile.get('red', 'threshold'))
        print('g_th:%s' % self.g_threshold)
        print('r_th:%s' % self.r_threshold)


def detect_color(filename):
    target_color = filename.split('_')[0]
    if target_color == 'r' or target_color == 'red':
        return 'red'
    if target_color == 'g' or target_color == 'green':
        return 'green'
    return 'green'


def main():
    s = Settings(args)
    for arg in args:
        print('arg:%s' % arg)
        fname = arg.split(s.delimiter)[-1]
        path = arg[:(-1 * len(fname))]
        dname = path
        output_dir = path
        fname_without_extention, filetype = os.path.splitext(fname)
        fname_without_suffix = re.sub(r'^[rg]_', '', fname_without_extention)
        print('filename:%s' % fname)
        print('path:%s' % path)
        print('filetype:%s' % filetype)

        if sys.platform.startswith('darwin') and path.find('Contents/MacOS') >= 0:
            s.parse_config(dname+'/../../../')
            with open('/tmp/zfmapper_log.txt', 'w') as f:
                f.write('configdir:'+str(dname)+'/../../../\r\n'+'args:'+str(args))
        elif filetype == '.exe' or filetype == '.py' or filetype == '':
            s.parse_config(dname)
        elif fname[0] == '.':
            pass
        else:
            print('Processing %s' % fname)

            # name, ext = os.path.splitext(fname)
            target_color = detect_color(fname_without_extention)
            if target_color == 'green':
                threshold = s.g_threshold
            if target_color == 'red':
                threshold = s.r_threshold

            # 画像読み込み
            img_tiff = imread('%s%s' % (dname, fname))

            # 8 bitに変換
            if(img_tiff.dtype!='uint8'):
                print('converting to uint8')
                img_tiff = (img_tiff/256).astype('uint8')

            # 結果格納配列
            data = {
                'x': [],
                'y': [],
                'r': [],
                'g': [],
                'b': [],
            }

            # ピクセル読み込み
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

            # 正規化
            data['x'] = data['x'] - xmin_tiff
            data['y'] = (data['y'] - ymin_tiff)
            if target_color == 'red':
                data['y'] = data['y'] * -1

            # データフレーム化
            df_tiff = pd.DataFrame(data=data)

            # CSVに書き出し
            df_tiff[['x', 'y', target_color[:1]]].to_csv('%s/%s_%s_th%s.csv' % (output_dir, fname_without_suffix, target_color, threshold), index=False, sep=',')


if __name__ == '__main__':
    main()
