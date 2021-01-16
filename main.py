import argparse
from pdftolatex.pdf import *

def main():
    """Function to take you from filepath to generated tex file"""
    if not os.path.isdir('localstore'):
        os.mkdir('localstore')
    
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help="Path to PDF in 'docs' folder")
    args = parser.parse_args()

    filepath = args.filepath
    filename = filepath.split('.')[0]

    pdf = PDF(filepath)
    texfile = TexFile(pdf)
    texfile.generate_tex_file(filename+'.tex')

if __name__ == "__main__":
    main()