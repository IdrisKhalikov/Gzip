from BinarySearchTree import BST
import unittest


class TestBinaryTree(unittest.TestCase):

    def assert_tree_state(self, tree, nodes):
        self.check_subtree(tree._arr, tree._root, nodes)

    def check_subtree(self, buffer, node, nodes):
        node_value = buffer[node.key]
        left = buffer[node.left.key] if node.left else None
        right = buffer[node.right.key] if node.right else None
        self.assertEqual(nodes[node_value], (left, right))
        if node.left != None:
            self.check_subtree(buffer, node.left, nodes)
        if node.right != None:
            self.check_subtree(buffer, node.right, nodes)

    def get_complex_tree(self):
        nodes = {
            6: (4, 8),
            4: (2, 5),
            2: (None, None),
            5: (None, None),
            8: (7, 9),
            7: (None, None),
            9: (None, None)
        }

        tree = (TreeBuilder()
                .insert(6,4,2,5,8,7,9))
        return tree, nodes

    def test_add_single_element(self):
        nodes = {
            0: (None, None)
        }
        tree = (TreeBuilder()
                .insert(0)
                .get_tree())

        self.assert_tree_state(tree, nodes)

    def test_add_multiple_elements(self):
        tree_builder, nodes = self.get_complex_tree() 
        self.assert_tree_state(tree_builder.get_tree(), nodes)

    def test_delete_element_with_no_children(self):
        tree_builder, nodes = self.get_complex_tree()
        tree = (tree_builder
                .delete(5)
                .get_tree())
        nodes.pop(5)
        nodes[4] = (2,None)
        self.assert_tree_state(tree, nodes)
    
    def test_delete_element_with_only_left_child(self):
        tree_builder, nodes = self.get_complex_tree()
        tree = (tree_builder
                .delete(5)
                .delete(4)
                .get_tree())
        nodes.pop(5)
        nodes.pop(4)
        nodes[6] = (2, 8)
        self.assert_tree_state(tree, nodes)

    def test_delete_element_with_only_right_child(self):
        tree_builder, nodes = self.get_complex_tree()
        tree = (tree_builder
                .delete(2)
                .delete(4)
                .get_tree())
        nodes.pop(2)
        nodes.pop(4)
        nodes[6] = (5, 8)
        self.assert_tree_state(tree, nodes)

    def test_delete_element_with_both_children(self):
        tree_builder, nodes = self.get_complex_tree()
        tree = (tree_builder
                .delete(4)
                .get_tree())
        nodes.pop(4)
        nodes[6] = (5, 8)
        nodes[5] = (2, None)
        self.assert_tree_state(tree, nodes)

class TreeBuilder:

    def __init__(self):
        self._buffer = []
        self._nodes = {}
        self._tree = BST(self._buffer, length=1)

    def insert(self, *values):
        for value in values:
            self._buffer.append(value)
            index = len(self._buffer) - 1
            _, _, node = self._tree.insert(index)
            self._nodes[value] = node
        return self

    def delete(self, *values):
        for value in values:
            self._tree.delete(self._nodes[value])
            self._nodes.pop(value)
        return self

    def get_tree(self):
        return self._tree
