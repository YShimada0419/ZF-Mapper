import os
import numpy as np
import pandas as pd
import tifffile

# 入力値: 処理する画像の入ったディレクトリ
dname = 'images'

for fname in os.listdir(dname):
    print('Processing %s'%fname)
    
    name, ext = os.path.splitext(fname)
    threshold = 50

    # 画像読み込み
    img_tiff = tifffile.imread('%s/%s'%(dname, fname))

    # 8 bitに変換
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

    valid_pix = np.array(range(l))[gs > threshold]
    data['y'] = valid_pix//img_tiff.shape[1]
    data['x'] = valid_pix%img_tiff.shape[1]
    data['r'] = rs[valid_pix]
    data['g'] = gs[valid_pix]
    data['b'] = bs[valid_pix]

    xmin_tiff = data['x'].min()
    ymin_tiff = data['y'][data['x'] == xmin_tiff].min()

    # 正規化
    data['x'] = data['x'] - xmin_tiff
    data['y'] = data['y'] - ymin_tiff

    # データフレーム化
    df_tiff = pd.DataFrame(data=data)

    # CSVに書き出し
    df_tiff[['x', 'y', 'g']].to_csv('%s_out.csv'%name, index=False, sep=',')
