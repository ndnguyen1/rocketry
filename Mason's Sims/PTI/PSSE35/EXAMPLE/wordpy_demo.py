#[wordpy_demo.py]  Demo for using functions from wordpy module
# ====================================================================================================
'''
'wordpy' module provides Pythonic Interface to Miscrosoft Word.
This module has functions to create new or update existing Microsoft Word document by:
- adding text into Word document
- inserting pictures/plots into Word document

This is an example file showing how to use various functions available in wordpy module.

---------------------------------------------------------------------------------
How to use this file?

As showed in __main__ (end of this file)
- Enable PSSE version specific environment, as an example:
    import psse35

- call any of the function as below
    run()  OR
    run(pssplt_eps_files, pict_files, docfile, outpath, show)
    You could modify various inputs in run)demo() as desired.

'''

# ====================================================================================================
import sys, os

def get_output_dir(outpath):
    # if called from PSSE's Example Folder, create report in subfolder 'Output_Pyscript'

    if outpath:
        outdir = outpath
        if not os.path.exists(outdir): os.mkdir(outdir)
    else:
        outdir = os.getcwd()
        cwd = outdir.lower()
        i = cwd.find('pti')
        j = cwd.find('psse')
        k = cwd.find('example')
        if i>0 and j>i and k>j:     # called from Example folder
            outdir = os.path.join(outdir, 'Output_Pyscript')
            if not os.path.exists(outdir): os.mkdir(outdir)

    return outdir

# ====================================================================================================

def get_output_filename(outpath, fnam):

    p, nx = os.path.split(fnam)
    if p:
        retvfile = fnam
    else:
        outdir = get_output_dir(outpath)
        retvfile = os.path.join(outdir, fnam)

    return retvfile

# ====================================================================================================

def run(pssplt_eps_files=[], pict_files=[], docfile='', outpath=None, show=True):
    """
Inputs:
pssplt_eps_files --> List of Multi-page 'eps' plot files created by PSSPLT
pict_files       --> List of any word compatible picture files (.eps, .wmf, .png, .bmp etc.)
docfile          --> Word file name
outpath          --> Outpath where Word file created/saved
Show             --> = True, Show Word
                     = False, Create and Save Word file but do not show
"""
    import wordpy

    pssplt_eps_files_lst = []
    for fnam in pssplt_eps_files:
        if not os.path.exists(fnam): continue
        pssplt_eps_files_lst.append(fnam)

    pict_files_lst   = []
    pict_caption_lst = []
    for fnam in pict_files:
        if not os.path.exists(fnam): continue
        p, nx = os.path.split(fnam)
        caption, x = os.path.splitext(nx)
        pict_files_lst.append(fnam)
        pict_caption_lst.append(caption)

    if  docfile:
        p, nx = os.path.split(docfile)
        docfnam, x = os.path.splitext(nx)
    else:
        docfnam = r'wordpy_demo_created'
        p = outpath

    # doc file
    docfile = get_output_filename(p, docfnam)

    docoverwrite = True

    # Picture Insert Options (see help(wordpy) for explaination)
    align      = 'center'
    captionpos = 'below'
    height     = None
    width      = None
    rotate     = None

    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    # Put-it-together
    wdobj = wordpy.workdoc(docfile=docfile, overwrite=docoverwrite)
    if show:
        wdobj.show()

    wdobj.page_format(orientation="portrait",left=0.75,right=0.75,top=0.5,bottom=0.5,
                      header=0.25,footer=0.25)

    wdobj.add_styled_para('Use of Python and Word','Title')

    txt = "This file is produced by Python script, by inserting picture files into word document. \
    It uses python module 'wordpy'.\n\n\
    This module is mainly created to add plot files (.eps, .png, .wmf etc.) \
    created by PSSPLT/PSSPLOT to existing or new Word files.\n\n\
    Use PSSPLT to create .eps files, and PSSPLOT to create .wmf files. Then use \
    'wordpy' module to create Word document from those files.\n\n\
    How to use it?\n\n\
    Use 'workdoc' function to create Miscrosoft Word object and use 'add_picture(...)' or \
    'add_pictures(...)' methods to insert pictures into the doc file.\n\n"
    wdobj.add_text(txt)

    txt = """Use either of the following to create Word object:
    (1) When file does not exist, create new file.
        wdobj = wordpy.workdoc()
    (2) When file exists, do not remove the content and add data at the end.
        wdobj = wordpy.workdoc(r"c:\working dir\ex1.doc", overwrite=False)
    (3) When file exists, remove the content and create new file.
        wdobj = wordpy.workdoc(r"c:\working dir\ex1.doc", overwrite=True)
    """
    wdobj.add_text(txt)


    if pssplt_eps_files_lst:
        wdobj.insert_page_break()
        wdobj.add_styled_para('Inserting multi-page PSSPLT EPS Files - add_pssplt_eps(...)','Heading 1')
        for fnam in pssplt_eps_files_lst:
            wdobj.add_pssplt_eps(fnam, captionlst=True, align=align, captionpos=captionpos,
                                 height=height, width=width, rotate=rotate)
            wdobj.insert_page_break()

    if pict_files_lst:
        wdobj.add_styled_para('Inserting One Picture File - add_picture(...)','Heading 1')
        wdobj.add_picture(pictfile=pict_files_lst[0], caption=pict_caption_lst[0], align=align,
                          captionpos=captionpos, height=None, width=None, rotate=0.0)
        wdobj.insert_page_break()

    if pict_files_lst:
        wdobj.add_styled_para('Inserting Many Picture Files - add_pictures(...)','Heading 1')
        wdobj.add_pictures(pictfilelst=pict_files_lst, captionlst=pict_caption_lst, align=align,
                           captionpos=captionpos, height=height, width=width, rotate=0.0)

    wdobj.save()

    if not show:
        txt = "\n Word file created:\n     {0}".format(wdobj.DOCFNAM)
        wdobj.close()
        print(txt)

# ====================================================================================================
# ====================================================================================================

if __name__ == '__main__':

    import psse35
    run()

# ====================================================================================================

