"""Assignment 2: Trees for Treemap

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all sub-directories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this asignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """
    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: Optional[str]
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        if name is None:
            self._subtrees = []
        else:
            self._subtrees = subtrees[:]
        self._parent_tree = None
        self._expanded = False
        self.data_size = 0
        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        if len(self._subtrees) == 0:
            self.data_size = data_size
        else:
            for sub in self._subtrees:
                sub._parent_tree = self
                self.data_size += sub.data_size

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        x, y, width, height = rect
        if self.data_size == 0:
            self.rect = (0, 0, 0, 0)
        elif self._subtrees == [] and self._name is not None:
            if width == 0 or height == 0:
                self.rect = (0, 0, 0, 0)
            else:
                self.rect = rect
        else:
            self.rect = rect
            prev = self._last_viable_tree()
            if width > height:
                self._recursive_width(prev, (x, y, width, height))
            else:
                self._recursive_height(prev, (x, y, width, height))

    def _recursive_width(self, prev: Optional[TMTree],
                         dims: Tuple[int, int, int, int]) -> None:
        """Recursive step for the treemap algorithm where width is greater than
        height
        """
        pos = dims[0]
        for sub in self._subtrees:
            scale = sub.data_size / self.data_size
            temp_width = int(dims[2] * scale)
            if sub == self._subtrees[-1] and (pos + temp_width) != \
                    (dims[0] + dims[2]):
                temp_width += (dims[0] + dims[2]) - (pos + temp_width)
            sub.rect = (pos, dims[1], temp_width, dims[3])
            pos += temp_width
            sub.update_rectangles(sub.rect)
            if self._subtrees[-1].data_size == 0 and prev is not None:
                x1, y1, width1, height1 = prev.rect
                temp = (dims[0] + dims[2]) - (x1 + width1)
                prev.rect = (x1, y1, width1 + temp, height1)
                prev.update_rectangles(prev.rect)

    def _recursive_height(self, prev: Optional[TMTree],
                          dims: Tuple[int, int, int, int]) -> None:
        """Recursive step for the treemap algorithm where height is greater than
        width
        """
        pos = dims[1]
        for sub in self._subtrees:
            scale = sub.data_size / self.data_size
            temp_height = int(dims[3] * scale)
            if sub == self._subtrees[-1] and (pos + temp_height) != \
                    (dims[1] + dims[3]):
                temp_height += (dims[1] + dims[3]) - (pos + temp_height)
            sub.rect = (dims[0], pos, dims[2], temp_height)
            pos += temp_height
            sub.update_rectangles(sub.rect)
            if self._subtrees[-1].data_size == 0 and prev is not None:
                x1, y1, width1, height1 = prev.rect
                temp = (dims[1] + dims[3]) - (y1 + height1)
                prev.rect = (x1, y1, width1, height1 + temp)
                prev.update_rectangles(prev.rect)

    def _last_viable_tree(self) -> TMTree:
        """Returns the last subtree of self that contributes to the area of the
        rectangle of self so that the full area is filled.
        """
        prev = None
        for previous in self._subtrees:
            if previous.data_size > 0:
                prev = previous
        return prev

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        ans = []
        if (self._expanded is False and self.data_size > 0) or \
                (self._subtrees == [] and self.data_size > 0):
            ans.append((self.rect, self._colour))
        else:
            if self.data_size == 0:
                return ans
            else:
                for sub in self._subtrees:
                    ans.extend(sub.get_rectangles())
        return ans

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        x, y, width, height = self.rect
        test = False
        if self._expanded is False:
            if x < pos[0] <= x + width and y < pos[1] <= y + height:
                test = True
        else:
            if self._subtrees:
                return self._recursive_get_position(pos)
        if test is True:
            return self
        return None

    def _recursive_get_position(self, position: Tuple[int, int]) \
            -> Optional[TMTree]:
        """Recursive step for get_tree_at_position.

        Returns either a TMTree or None
        """
        checker = []
        for subtree in self._subtrees:
            checker.append(subtree.get_tree_at_position(position))
        if checker.count(None) == len(checker):
            return None
        for item in checker:
            if item is not None:
                return item
        return None

    def _get_leaves_list(self) -> List[TMTree]:
        """Returns a list of TMTrees that are leaves of the tree self
        """
        ans = []
        if self._subtrees == [] and self.data_size > 0:
            ans.append(self)
        else:
            for sub in self._subtrees:
                ans.extend(sub._get_leaves_list())
        return ans

    def _get_ancestor_list(self) -> List[TMTree]:
        """Returns a list of the ancestors of a given tree
        """
        ans = []
        if self._parent_tree is None:
            return ans
        else:
            ans.append(self._parent_tree)
            ans.extend(self._parent_tree._get_ancestor_list())
        return ans

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        leaves = self._get_leaves_list()
        if self in leaves:
            return self.data_size
        else:
            self.data_size = 0
            for subtree in self._subtrees:
                self.data_size += subtree.update_data_sizes()
        return self.data_size

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        leaves = self._get_leaves_list()
        if self in leaves:
            if destination._subtrees:
                destination._subtrees.append(self)
                self._parent_tree.data_size -= self.data_size
                self._parent_tree._subtrees.remove(self)
                self._parent_tree = destination

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """
        leaves = self._get_leaves_list()
        if self in leaves:
            if factor < 0:
                temp = math.floor(factor * self.data_size)
            else:
                temp = math.ceil(factor * self.data_size)
            if self.data_size + temp > 0:
                self.data_size += temp

    def _get_all_subtrees(self) -> List[TMTree]:
        """Returns a list of every descendant of self.
        """
        ans = []
        if not self._subtrees:
            ans.append(self)
        else:
            for items in self._subtrees:
                if items not in ans:
                    ans.append(items)
                ans.extend(items._get_all_subtrees())
        return ans

    def expand(self) -> None:
        """Sets the _expanded attribute of self to True and all of its
        descendants.
        """
        if self._subtrees:
            self._expanded = True
            ancestor = self._get_ancestor_list()
            for tree in ancestor:
                tree._expanded = True

    def expand_all(self) -> None:
        """Sets the _expanded attribute of every descendant of self that is an
        internal node to True.
        """
        temp = self._get_all_subtrees()
        self._expanded = True
        for item in temp:
            item.expand()

    def collapse(self) -> None:
        """Sets the _expanded attribute of the parent of self,
         and all descendants of that parent to False.
        """
        prev = self._parent_tree
        if prev is not None:
            prev._expanded = False
            for items in prev._get_all_subtrees():
                items._expanded = False

    def collapse_all(self) -> None:
        """Sets the _expanded attribute of every tree in the data_tree to False.
        """
        if self._parent_tree is not None:
            self.collapse()
            self._parent_tree.collapse_all()

    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        sub = []
        if not os.path.isdir(path):
            TMTree.__init__(self, os.path.basename(path), [],
                            os.path.getsize(path))
        else:
            for filename in os.listdir(path):
                sub.append(FileSystemTree(os.path.join(path, filename)))
            TMTree.__init__(self, os.path.basename(path), sub, 0)

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
