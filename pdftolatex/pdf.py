#pdf.py

import numpy as np
import pdf2image
import os
import cv2
import pytesseract
from tqdm import tqdm

from pdftolatex.utils import *
from pdftolatex.segment_pdf import *
from pdftolatex.latex import *

local_store_folder = "localstore"

class PDF():
    """PDF Object which represents a PDF. Contains Page objects."""

    def __init__(self, filepath):
        """Input: Filename of PDF with '.pdf' extension contained within input_folder"""
        self.path = filepath
        self.name = get_file_name(os.path.basename(filepath))
        self.pages = self.pdftopages(self.path)
        self.asset_folder = os.path.join(local_store_folder, self.name + 'assets')
        os.mkdir(self.asset_folder)
        self.num_figs = 0

    def pdftopages(self, path):
        """Input: PDF Filepath, Output: List of Page objects."""
        pil_pages = pdf2image.convert_from_path(path)
        save_pil_images(pil_pages, os.path.join(local_store_folder, self.name + "pages"))
        page_imgs = [cv2.cvtColor(np.asarray(p), cv2.COLOR_RGB2BGR) for p in pil_pages]
        print(f"Segmenting pages for {self.name}...")
        return [Page(page_img, self) for page_img in tqdm(page_imgs)]
    
    def generate_latex(self):
        """Output: List of Latex objects containing content in order of appearance in PDF."""
        content = []
        print(f"Generating LaTex... for {self.name}")
        for page in tqdm(self.pages):
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
        """Output: List of Block objects"""
        bboxes = find_content_blocks(self.page_img)
        return [Block(bbox, self) for bbox in bboxes]

    def generate_latex(self):
        """Output: List of Latex objects containing content in order of apperance on page"""
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
        """Input: BBox object, Output: cv2 image"""
        return self.parent_page.page_img[bbox.y:bbox.y_bottom, :]

    def generate_latex(self):
        """Output: A singular Latex object (within a list) containing block's content"""
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
        """Output: Tuple with block type at index 1, block content as string at index 2."""
        data_dict = pytesseract.image_to_data(self.block, output_type=pytesseract.Output.DICT)
        confs = [abs(int(c)) for c in data_dict['conf']]
        if np.mean(confs) > 40:
            s = ""
            for word in data_dict['text']:
                s += word + " "
            return (0, s)
        else:
            return (1, '--Block Type is Figure--')
    
