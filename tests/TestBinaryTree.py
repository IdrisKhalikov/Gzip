from FastBST import FastBST
from unittest.mock import patch
import unittest

class TestBinaryTree(unittest.TestCase):

    def checkTreeState(self, tree, nodes):
        for node in nodes:
            left, right = nodes[node]
            possible_nodes = [tree._right_son[tree._parent[node]]]
            if tree._parent[node] < len(tree._left_son):
                possible_nodes.append(tree._left_son[tree._parent[node]])

            self.assertIn(node, possible_nodes)
            self.assertTrue(tree._left_son[node] == left)
            self.assertTrue(tree._right_son[node] == right)
    
    def build_tree(self, expected_nodes, insert_order):
        array = []
        node_positions = {}
        for index, item in enumerate(insert_order):
            array.append(1)
            array.append(item)
            node_positions[item] = index*2
        check_nodes = {}
        tree = FastBST(array, 2)
        for item in insert_order:
            index = node_positions[item]
            tree.insert(index)
            left, right = expected_nodes[item]
            left = node_positions[left] if left != -1 else tree._not_used
            right = node_positions[right] if right != -1 else tree._not_used
            check_nodes[index] = (left, right)
        return tree, check_nodes

    def get_complex_tree(self):
        nodes = {
            6 : (4,8),
            4 : (2,5),
            2 : (-1,-1),
            5 : (-1,-1),
            8 : (7, 9),
            7 : (-1,-1),
            9 : (-1, -1)
        }
        return self.build_tree(nodes, [6,4,2,5,8,7,9])

    def testAddSingleElement(self):
        nodes = {
            0 : (-1, -1)
        }
        tree, expected_nodes = self.build_tree(nodes, [0])
        self.checkTreeState(tree, expected_nodes)

    def testAddMultipleElements(self):
        self.checkTreeState(*self.get_complex_tree())