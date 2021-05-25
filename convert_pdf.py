import argparse
from pdftolatex.pdf import *

def convert(filepath):
    """Convert pdf at filepath to .tex file"""
    if not os.path.isdir('localstore'):
        os.mkdir('localstore')

    if os.path.isdir(filepath):
        for f in os.listdir(filepath):
            convert(f)
    
    filename = get_file_name(filepath)
    pdf = PDF(filepath)
    texfile = TexFile(pdf)
    texfile.generate_tex_file(filename+".tex")


def main():   
    parser = argparse.ArgumentParser(description="Generate a .tex file from a .pdf file.")
    parser.add_argument('--filepath', type=str, help="Path to pdf to be converted")
    parser.add_argument('--folderpath', type=str, help="Path to folder containing pdfs to be converted. All pdfs in the folder will be converted")
    
    args = parser.parse_args()

    filepath = args.filepath
    folderpath = args.folderpath

    if folderpath:
        convert(folderpath)
    else:
        convert(filepath)

if __name__ == "__main__":
    main()