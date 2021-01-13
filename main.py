import argparse
from pdf import *

def main():
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