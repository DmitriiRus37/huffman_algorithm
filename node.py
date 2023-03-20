class Node:
    def __init__(self, **kwargs):
        id = None
        if 'letter' in kwargs and 'freq' in kwargs:
            self.letter = kwargs['letter']
            self.freq = kwargs['freq']
            self.left = None
            self.right = None
        elif 'left' in kwargs and 'right' in kwargs:
            self.left = kwargs['left']
            self.right = kwargs['right']
            self.freq = self.left.freq + self.right.freq