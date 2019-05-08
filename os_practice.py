import os
import math
from tm_trees import FileSystemTree
from papers import PaperTree

s = PaperTree('CS1', [], all_papers=True)
s.update_rectangles((0, 0, 1800, 900))
# print(s._subtrees[1]._subtrees[2].data_size)
r = FileSystemTree('example-directory')
r.update_rectangles((0, 0, 1800, 900))
s.expand_all()
r.expand_all()
print(r.get_rectangles())
print(''
      ''
      ''
      ''
      ''
      ''
)
print(len(s.get_rectangles()))



