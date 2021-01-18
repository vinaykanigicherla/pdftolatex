#segment_pdf.py

import numpy as np
import cv2
import matplotlib.pyplot as plt

from pdftolatex.utils import *

def segment(img):
    """"Input: cv2 image of page. Output: BBox objects for content blocks in page"""
    MIN_TEXT_SIZE = 10
    HORIZONTAL_POOLING = 25
    img_width = img.shape[1]
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 5)
    
    blur = cv2.GaussianBlur(img_bw, (7,7), 0) 
    
    #simple_plot(blur)

    k1 = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    m1 = cv2.morphologyEx(blur, cv2.MORPH_GRADIENT, k1)
    
    #simple_plot(m1)
    
    k2 = cv2.getStructuringElement(cv2.MORPH_RECT, (HORIZONTAL_POOLING, 5))
    m2 = cv2.morphologyEx(m1, cv2.MORPH_CLOSE, k2)

    #simple_plot(m2)    

    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    m3 = cv2.dilate(m2, k3, iterations=2)
    
    #simple_plot(m3)

    contours = cv2.findContours(m3, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    
    bboxes = []
    for c in contours:
        
        bx,by,bw,bh = cv2.boundingRect(c)
        
        if bh < MIN_TEXT_SIZE:
            continue

        if not pct_white(img[by:by+bh, bx:bx+bw]) < 1:
            continue 
    
        bboxes.append(BBox(0, by, img_width, bh))        
    
    return sorted(bboxes, key=lambda x: x.y)


def process_bboxes(bboxes):
    """"Input and Output: List of BBox objects. BBox post-processing to remove redundancy"""
    bboxes = remove_duplicate_bboxes(bboxes)
    bboxes = merge_bboxes(bboxes)
    
    #Fix BBox overlap 
    for i in range(len(bboxes)-1):
        curr_box, next_box = bboxes[i], bboxes[i+1]
        if curr_box.y_bottom > next_box.y:
            new_y = (curr_box.y_bottom + next_box.y)/2
            curr_box.y_bottom, next_box.y = int(new_y), int(new_y)

    return bboxes

def find_content_blocks(img):
    """"Find all content blocks in page."""
    return process_bboxes(segment(img))

def test(segment_method):
    """"Test method. Visualizes segment method on images in test_dir"""
    test_dir = 'test_ims_1'
    boxes_dict = {}

    for im_file in os.listdir(test_dir):
        img = cv2.imread(os.path.join(test_dir, im_file)) 
        boxes = segment_method(img)
        imb = plot_all_boxes(img, boxes)
        plt.imshow(imb)
        plt.show()
        boxes_dict[im_file] = boxes
        
    return boxes_dict


