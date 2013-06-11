import os
from ntfslink import hardlinks

hardlinks.example(os.path.abspath(__file__))
