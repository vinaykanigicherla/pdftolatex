import numpy as np
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt

#Image Processing related

def save_pil_images(items, path):
    """Save  PIL Image items to folder specified by path."""
    if not os.path.isdir(path):
        os.mkdir(path)
        for idx, item in enumerate(items):
            save_path = os.path.join(path, str(idx)+".jpg")
            item.save(save_path)

class BBox():
    """BBox object representing boundingrectangle. (x coord of top-left, y coord of top-left, wdith, height)"""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.y_bottom = y + height


def pct_white(img):
    """Find percentage of white pixels in img."""
    if len(img.shape) == 3:
        b, g, r = cv2.split(img)
        wb, wg, wr = b==255, g==255, r==255
        white_pixels = np.bitwise_and(wb, np.bitwise_and(wg, wr))
        white_count, imsize = np.sum(white_pixels), img.size/3
    elif len(img.shape) == 2:
        white_pixels = img == 255
        white_count, imsize = np.sum(white_pixels), img.size
    return white_count/imsize

def simple_plot(img):
    """Plot img using matplotlib.pyplot"""
    plt.imshow(img)
    plt.show()


def plot_all_boxes(img, boxes):
    """Plots all rectangles from boxes onto img."""
    copy = img.copy()
    alpha = 0.4
    for box in boxes:
       x, y, w, h = box.x, box.y, box.width, box.height
       rand_color = list(np.random.random(size=3) * 256)
       cv2.rectangle(copy, (x, y), (x+w, y+h), rand_color, -1)
    
    img_new = cv2.addWeighted(copy, alpha, img, 1-alpha, 0)
    return img_new

def remove_duplicate_bboxes(boxes):
    """Remove bounding boxes from a list that start at the same y-coord"""
    new = []
    [new.append(box) for box in boxes if not new or box.y not in [b.y for b in new]]
    return new

def merge_bboxes(lst):
        new = []
        [new.append(box) for box in lst if not new or 
                not any([box.y > box2.y and box.y_bottom < box2.y_bottom for box2 in new])]
        return new

def expand_bbox(box, expand_factor):
    x, y, w, h = box.x, box.y, box.width, box.height
    expansion = int(min(h, w) * expand_factor)
    x = max(0, x-expansion)
    y = max(0, y-expansion)
    h, w = h + (2*expansion), w + (2*expansion)

    return BBox(x, y, w, h) 




#Latex related 

get_file_name = lambda x: x.split('.')[0]

def escape_special_chars(s):
    """Return string s with LaTex special characters escaped."""
    special_chars = ['&', '%', '$', '#', '_', '{', '}']
    for c in special_chars:
        s = s.replace(c, '\\' + c) if c in s else s
    return s

def make_strlist(lst):
    """Make all the items of a lst a string"""
    return [str(i) for i in lst]

def write_all(filename, lst):
    """Write all the strings contained in lst to filename"""
    f = open(filename, 'a')
    for s in lst:
        f.write('\n')
        f.write(s)
        f.write('\n')
    f.close()
    print("Wrote {0} strings to {1}".format(len(lst), filename))

