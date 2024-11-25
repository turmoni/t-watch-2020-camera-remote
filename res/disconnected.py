# Adapted from 'signal_disconnected' in https://fonts.google.com/icons

HEIGHT = 80
WIDTH = 80
COLORS = 2
BITS = 6400
BPP = 1
PALETTE = [0x55ad,0x0000]
_bitmap =\
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'\
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'\
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'\
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'\
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'\
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x3f\xff\xff\xff\xff'\
b'\xff\xfe\xff\xff\xfe\x1f\xff\xff\xff\xff\xff\xfc\x7f\xff\xfc\x0f'\
b'\xff\xff\xff\xff\xff\xf8\x3f\xff\xf8\x07\xff\xff\xff\xff\xff\xf0'\
b'\x1f\xff\xf0\x03\xff\xff\xff\xff\xff\xe0\x0f\xff\xf0\x01\xff\xff'\
b'\xff\xff\xff\xf0\x0f\xff\xf8\x00\xff\xff\xff\xff\xff\xf0\x07\xff'\
b'\xfc\x00\x7f\xff\xff\xff\xff\xf8\x07\xff\xfe\x00\x3f\xff\xff\xff'\
b'\xfe\xfc\x03\xff\xff\x00\x1f\xff\xff\xff\xfc\x7e\x01\xff\xff\x80'\
b'\x0f\xff\xff\xff\xf8\x3e\x01\xff\xff\x80\x07\xff\xff\xff\xf0\x1f'\
b'\x01\xff\xff\x00\x03\xff\xff\xff\xe0\x0f\x00\xff\xff\x00\x01\xff'\
b'\xff\xff\xf0\x0f\x80\xff\xff\x00\x00\xff\xff\xff\xf0\x07\x80\xff'\
b'\xfe\x00\x00\x7f\xff\xff\xf8\x07\xc0\x7f\xfe\x02\x00\x3f\xf0\x0f'\
b'\xfc\x07\xc0\x7f\xfe\x03\x00\x1f\xe0\x03\xfc\x03\xc0\x7f\xfe\x03'\
b'\x80\x0f\xf0\x01\xfe\x03\xc0\x7f\xfe\x07\xc0\x07\xf8\x00\xfe\x03'\
b'\xe0\x7f\xfc\x07\x80\x03\xfc\x00\xff\x01\xe0\x3f\xfc\x07\x80\x01'\
b'\xfe\x00\xff\x01\xe0\x3f\xfc\x07\x80\x00\xff\x00\x7f\x01\xe0\x3f'\
b'\xfc\x07\x80\x00\x7f\x80\x7f\x01\xe0\x3f\xfc\x07\x80\x00\x3f\xc0'\
b'\x7f\x01\xe0\x3f\xfc\x07\x80\x00\x1f\xe0\x7f\x01\xe0\x3f\xfc\x07'\
b'\x80\x80\x0f\xf0\x7f\x01\xe0\x3f\xfc\x07\x80\xc0\x07\xf8\xff\x01'\
b'\xe0\x3f\xfc\x07\xc0\x60\x03\xfc\xfe\x03\xe0\x3f\xfe\x07\xc0\x70'\
b'\x01\xff\xfe\x03\xe0\x7f\xfe\x03\xc0\x78\x00\xff\xfe\x03\xc0\x7f'\
b'\xfe\x03\xc0\x3c\x00\x7f\xfc\x03\xc0\x7f\xfe\x03\xe0\x3e\x00\x3f'\
b'\xfc\x07\xc0\x7f\xfe\x01\xe0\x1f\x00\x1f\xf8\x07\xc0\x7f\xff\x01'\
b'\xf0\x0f\x80\x0f\xf0\x0f\x80\xff\xff\x01\xf0\x07\xc0\x07\xf8\x0f'\
b'\x80\xff\xff\x00\xf8\x07\xe0\x03\xfc\x1f\x00\xff\xff\x80\xf8\x0f'\
b'\xf0\x01\xfe\x1f\x01\xff\xff\x80\x7c\x1f\xf0\x00\xff\x3e\x01\xff'\
b'\xff\xc0\x7e\x3f\xf0\x00\x7f\xfc\x03\xff\xff\xc0\x3f\xff\xf0\x00'\
b'\x3f\xfc\x03\xff\xff\xe0\x1f\xff\xf0\x00\x1f\xf8\x07\xff\xff\xe0'\
b'\x0f\xff\xf0\x00\x0f\xf8\x07\xff\xff\xf0\x07\xff\xf0\x00\x07\xf8'\
b'\x0f\xff\xff\xf8\x07\xff\xf0\x00\x03\xfc\x1f\xff\xff\xf8\x0f\xff'\
b'\xf0\x00\x01\xfe\x1f\xff\xff\xfc\x1f\xff\xf0\x08\x00\xff\x3f\xff'\
b'\xff\xfe\x3f\xff\xf0\x0c\x00\x7f\xff\xff\xff\xff\xff\xff\xf0\x0e'\
b'\x00\x3f\xff\xff\xff\xff\xff\xff\xf0\x0f\x00\x1f\xff\xff\xff\xff'\
b'\xff\xff\xf0\x0f\x80\x0f\xff\xff\xff\xff\xff\xff\xf0\x0f\xc0\x07'\
b'\xff\xff\xff\xff\xff\xff\xf0\x0f\xe0\x03\xff\xff\xff\xff\xff\xff'\
b'\xf0\x0f\xf0\x01\xff\xff\xff\xff\xff\xff\xf0\x0f\xf8\x00\xff\xff'\
b'\xff\xff\xff\xff\xf0\x0f\xfc\x00\x7f\xff\xff\xff\xff\xff\xf0\x0f'\
b'\xfe\x00\x3f\xff\xff\xff\xff\xff\xf0\x0f\xff\x00\x1f\xff\xff\xff'\
b'\xff\xff\xf0\x0f\xff\x80\x0f\xff\xff\xff\xff\xff\xf0\x0f\xff\xc0'\
b'\x07\xff\xff\xff\xff\xff\xf0\x0f\xff\xe0\x03\xff\xff\xff\xff\xff'\
b'\xff\xff\xff\xf0\x01\xff\xff\xff\xff\xff\xff\xff\xff\xf8\x01\xff'\
b'\xff\xff\xff\xff\xff\xff\xff\xfc\x03\xff\xff\xff\xff\xff\xff\xff'\
b'\xff\xfe\x07\xff\xff\xff\xff\xff\xff\xff\xff\xff\x0f\xff\xff\xff'\
b'\xff\xff\xff\xff\xff\xff\x9f\xff\xff\xff\xff\xff\xff\xff\xff\xff'\
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'\
b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
BITMAP = memoryview(_bitmap)
