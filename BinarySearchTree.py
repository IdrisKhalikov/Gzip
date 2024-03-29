'''По сути обычное двоичное дерево поиска, слегка модифицтрованное под наши задачи.
Сущности дерева и узлов разделил, чтобы каждый раз при вызове различных методов не передавать массив.
Здесь значения в узлах - начальные индексы подстрок в массиве'''

'''Чтобы немного оптимизировать поиск подстроки, 
вместо одного дерева создаем 256 по одному на каждый возможный символ в начале строки'''

class BSTArray:
    def __init__(self, arr, lookahead):
        self._arr = arr
        self._trees = [BST(arr, lookahead) for _ in range(256)]
        self._nodes = [None]*len(arr)
    
    def insert(self, index):
        match_len, match_index, node =  self._trees[self._arr[index]].insert(index)
        self._nodes[index] = node
        return match_len, match_index

    def delete(self, index):
        if self._nodes[index] is None:
            return
        self._trees[self._arr[index]].delete(self._nodes[index])


class BST:
    def __init__(self, array, length):
        self._root = Node()
        self._arr = array
        self._length = length

    '''Функция сравнивает две подстроки по индексам в массиве.
    Первый элемент кортежа - результат сравнения, второй - длина совпадения'''

    def _compare(self, a, b):
        for i in range(self._length):
            if (result := self._arr[a + i] - self._arr[b + i]) != 0:
                break
        return (result, i)

    '''Функция добавляет подстроку, представленную в виде индекса ее начала, в дерево
    и возвращает наибольшее совпадение в виде (длина, индекс).'''

    def insert(self, key):
        node = self._root
        if node.key is None:
            node.key = key
        max_match_len = 0
        max_match_index = 0
        while node.key != key:
            parent_node = node
            cmp, match_len = self._compare(key, node.key)
            if match_len >= max_match_len:
                max_match_index = node.key
                max_match_len = match_len
            if cmp < 0:
                if node.left is None:
                    node.left = Node(key, parent_node)
                node = node.left
            elif cmp >= 0:
                if node.right is None:
                    node.right = Node(key, parent_node)
                node = node.right
        return max_match_len, max_match_index, node

    '''Удаляет узел, принимает в качестве аргумента сам узел.
    Такая реализация сдеалана, чтобы не тратить время на поиск узла, как в случае с удалением по индексу.
    При добавлении узла он сохраняется в массив, откуда при необходимости удаляется.'''
    def delete(self, node):
        if node == None:
            return
        parent = node.parent
        substitute = None
        if node.left is None or node.right is None:
            if not node.left:
                substitute = node.right
            if not node.right:
                substitute = node.left
        else:
            new_node = node.right
            new_node_parent = None
            while new_node.left != None:
                new_node_parent = new_node
                new_node = new_node.left
            if new_node_parent is not None:
                new_node_parent.left = new_node.right
                self._update_node(new_node_parent)
            else:
                node.right = new_node.right
                self._update_node(node)
            substitute = new_node

        if substitute is not None:
            if substitute.parent.left is substitute:
                substitute.parent.left = None
            else:
                substitute.parent.right = None
            substitute.parent = parent
            substitute.left = node.left
            substitute.right = node.right
            self._update_node(substitute)
        if node is self._root:
            if substitute is None:
                self._root = Node()
            else:
                self._root = substitute
            return
        if parent.left is node:
            parent.left = substitute
        else:
            parent.right = substitute
        self._remove_node(node)

    def _remove_node(self, node):
        node.left = None
        node.right = None
        node.parent = None

    def _update_node(self, node):
        if node.left is not None:
            node.left.parent = node
        if node.right is not None:
            node.right.parent = node

    def get_nodes(self, func, node=None):
        if node is None:
            node = self._root
        if node.left:
            yield from self.get_nodes(func, node.left)
        yield node.key
        if node.right:
            yield from self.get_nodes(func, node.right)


class Node:

    def __init__(self, key=None, parent_node=None):
        self.key = key
        self.parent = parent_node
        self.left = None
        self.right = None
