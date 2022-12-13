import os

SAVEDIR = os.path.join(os.getcwd(), 'results')

if not os.path.isdir(SAVEDIR):
    os.mkdir(SAVEDIR)
