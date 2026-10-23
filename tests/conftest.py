import os

# render Qt widgets without a display
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
