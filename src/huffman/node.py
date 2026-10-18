class Node:
    def __init__(self, **kwargs):
        if 'letter' in kwargs and 'freq' in kwargs:
            self.letter = kwargs['letter']
            self.freq = kwargs['freq']
            self.left = None
            self.right = None
        elif 'left' in kwargs and 'right' in kwargs:
            self.left = kwargs['left']
            self.right = kwargs['right']
            self.freq = 0 if self.left is None or self.right is None else self.left.freq + self.right.freq
            self.letter = None
        elif 'letter' in kwargs and 'code' in kwargs:
            self.left = None
            self.right = None
            self.code = kwargs['code']
            self.letter = kwargs['letter']