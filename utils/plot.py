import sys

from lib.reader import StreamReader

sr = StreamReader()
f = sr.read(sys.argv[1])
f.plot()
