#pdf.py

import numpy as np
import pdf2image
import os
import cv2
import pytesseract

from utils import * 
from segment_pdf import *
from latex import *

local_store_folder = "localstore"
input_folder = "docs"

class PDF():
    """PDF Object which represents a PDF. Contains Page objects."""

    def __init__(self, filename):
        """Input: Filename of PDF with '.pdf' extension contained within input_folder"""
        self.path = os.path.join(input_folder, filename)
        self.name = filename.split('.')[0]
        self.pages = self.pdftopages(self.path)
        self.asset_folder = os.path.join(local_store_folder, self.name + 'assets')
        os.mkdir(self.asset_folder)
        self.num_figs = 0

    def pdftopages(self, path):
        """Input: PDF Filepath, Output: List of Page objects."""
        pil_pages = pdf2image.convert_from_path(path)
        save_pil_images(pil_pages, os.path.join(local_store_folder, self.name + "pages"))
        page_imgs = [cv2.cvtColor(np.asarray(p), cv2.COLOR_RGB2BGR) for p in pil_pages]
        return [Page(page_img, self) for page_img in page_imgs]
    
    def generate_latex(self):
        content = []
        for page in self.pages:
            content.extend(page.generate_latex())
        
        graphics_command = Command('graphicspath', [os.path.join(os.getcwd(), self.asset_folder)])
        
        return [graphics_command] + [Environment(content, 'document')] 

class Page():
    """Page obejct representing a page. Contains Block objects."""
    def __init__(self, page_img, pdf):
        """Input: cv2 image of the page. Its a numpy array."""
        self.page_img = page_img
        self.parent_pdf = pdf
        self.height = page_img.shape[0]
        self.width = page_img.shape[1]
        self.blocks = self.generate_blocks()

    def generate_blocks(self):
        bboxes = find_content_blocks(self.page_img)
        return [Block(bbox, self) for bbox in bboxes]

    def generate_latex(self):
        content = []
        for block in self.blocks:
            content.extend(block.generate_latex())
        return content + [Command('par'), Command('vspace', arguments = ['10pt'])]


class Block():
    """Block object representing portion of a Page containing a certain type of content. Content can be text, image. (to add: math equation, table, matrix, ...)"""
    def __init__(self, bbox, parent_page):
        """Input: cv2 image of page containing the block, BBox object descrbing position"""
        self.parent_page = parent_page
        self.bbox = bbox
        self.block = self.make_block(bbox)
        self.block_type, self.content_string = self.determine_content() #0:Text, 1:Fig

    def make_block(self, bbox):
        """Input: BBox object"""
        return self.parent_page.page_img[bbox.y:bbox.y_bottom, :]

    def generate_latex(self):
        if self.block_type == 0:
            return [Text(self.content_string), Command('vspace', arguments=['10pt'])]

        elif self.block_type == 1:
            figure_dir = self.parent_page.parent_pdf.asset_folder
            fig_path = os.path.join(figure_dir, 
                    str(self.parent_page.parent_pdf.num_figs)+'.jpg')
            cv2.imwrite(fig_path, self.block)
            self.parent_page.parent_pdf.num_figs += 1
            fig_env_content = [Command('includegraphics', arguments=[os.path.join(os.getcwd(), fig_path)], options=[('width', Command('textwidth'))]), 
                                Command('centering')] 
            return [Environment(fig_env_content, 'figure', options=[('', 'h')])]

    def determine_content(self):
        data_dict = pytesseract.image_to_data(self.block, output_type=pytesseract.Output.DICT)
        confs = [abs(int(c)) for c in data_dict['conf']]
        print('conf_mean: ', np.mean(confs))
        if np.mean(confs) > 40:
            s = ""
            for word in data_dict['text']:
                s += word + " "
            return (0, s)
        else:
            return (1, '--Block Type is Figure--')
    
