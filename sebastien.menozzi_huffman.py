__license__ = 'GolluM & Junior (c) EPITA'
__docformat__ = 'reStructuredText'
__revision__ = '$Id: huffman.py 2018-04-24'

"""
Huffman homework
2018
@author: sebastien.menozzi
"""

from algopy import bintree
from algopy import heap

################################################################################
## COMPRESSION

"""
Creates a list with a certain length and certain values
"""
def __initlist(n, val):
    L = []
    for i in range(n):
        L.append(val)
    return L

"""
Creates an histogram from a string
"""
def __hist(s):
    H = __initlist(256, 0)
    for c in s:
        H[ord(c)] += 1;
    return H;

def buildfrequencylist(dataIN):
    """
    Builds a tuple list of the character frequencies in the input.
    """
    freq = []
    H = __hist(dataIN);
    i = 0;
    for c in H:
        if c != 0:
            freq.append((c, chr(i)))
        i += 1
    return freq

def __delete(list, pos):
    i = 0;
    result = [];
    for e in list:
        if (i != pos):
            result.append(e);
        i += 1;
    return result;

"""
    Builds a tuple list of the character frequencies in the input.
"""

def __getPosMinFreqTree(frequencytree):
    """
    Get the position of the minimun frequency tree 
    """
    length_frequencytree = len(frequencytree)

    minTree = frequencytree[0]
    pos = 0

    i = 1
    while (i < length_frequencytree):
        tree = frequencytree[i]
        if tree.key[0] < minTree.key[0]:
            pos = i
            minTree = tree
        i += 1
    return pos

def __buildfrequencytree(frequency):
    frequencytree = []
    for key in frequency:
        node = (key[0], key[1])
        frequencytree.append(bintree.BinTree(node, None, None))
    return frequencytree

def __mergeMinTrees(minTree1, minTree2):
    """
    Merge the two minimun trees
    """
    return bintree.BinTree((minTree1.key[0] + minTree2.key[0], None), minTree2, minTree1)

def __rebuildWithoutFrequency(frequencytree):
    """
    Rebuild the tree without the tuple
    """
    if frequencytree == None:
        return None
    else:
        huffmantree = bintree.BinTree(frequencytree.key[1], None, None)
        huffmantree.left = __rebuildWithoutFrequency(frequencytree.left)
        huffmantree.right = __rebuildWithoutFrequency(frequencytree.right)
        return huffmantree

def buildHuffmantree(inputList):
    """
    Processes the frequency list into a Huffman tree according to the algorithm.
    """
    frequencytree = __buildfrequencytree(inputList)

    while len(frequencytree) != 1:
        i = __getPosMinFreqTree(frequencytree)
        minTree1 = frequencytree[i]
        frequencytree = __delete(frequencytree, i)

        i = __getPosMinFreqTree(frequencytree)
        minTree2 = frequencytree[i]
        frequencytree = __delete(frequencytree, i)

        frequencytree.append(__mergeMinTrees(minTree1, minTree2))

    return __rebuildWithoutFrequency(frequencytree[0])

def __huffmanTreeToEncodeData(huffmanTree, trace, encodeList):
    if (huffmanTree.left == None and huffmanTree.right == None):
        encodeList[huffmanTree.key] = trace
    if (huffmanTree.left != None):
        __huffmanTreeToEncodeData(huffmanTree.left, trace + "0", encodeList)
    if (huffmanTree.right != None):
        __huffmanTreeToEncodeData(huffmanTree.right, trace + "1", encodeList)
    return encodeList

def encodedata(huffmanTree, dataIN):
    """
    Encodes the input string to its binary string representation.
    """
    encodeList = __huffmanTreeToEncodeData(huffmanTree, "", {})
    result = ""

    for c in dataIN:
        result += encodeList[c]
    return result

def __removebits(n, align):
    result = ""
    i = 0
    for b in n:
        if (i == align):
            result += b
        else:
            i += 1
    return result

def __encodeIn8bits(s):
    length_s = len(s)

    if (length_s < 8):
        while (length_s < 8):
            s = "0" + s
            length_s += 1
        return s
    if (length_s > 8):
        return __removebits(s, length_s - 8)
    return s


def __dec2bin(n):
    if n < 0:
        raise Exception("Must be a positive number")
    elif n == 0:
        return '0'
    else:
        return __dec2bin(n // 2) + str(n % 2)

def __huffmanTreeToEncodeTree(huffmanTree, result):
    if (huffmanTree.left == None and huffmanTree.right == None):
        result += '1' + __encodeIn8bits(__dec2bin(ord(huffmanTree.key)))
    if (huffmanTree.left != None):
        result += '0'
        __huffmanTreeToEncodeTree(huffmanTree.left, result)
    if (huffmanTree.right != None):
        __huffmanTreeToEncodeTree(huffmanTree.right, result)
    return result

def encodetree(huffmanTree):
    """
    Encodes a huffman tree to its binary representation using a preOrder traversal:
        * each leaf key is encoded into its binary representation on 8 bits preceded by '1'
        * each time we go left we add a '0' to the result
    """
    encodeTreeList = __huffmanTreeToEncodeTree(huffmanTree, [])
    result = ""

    for c in encodeTreeList:
        result += c
    return result

def __binary_to_int(binary_string):
    n = 0
    for char in binary_string:
        n *= 2
        if char == '1':
            n += 1
    return n

def tobinary(dataIN):
    """
    Compresses a string containing binary code to its real binary value.
    """
    binary = ""
    octet = ""
    length_dataIN = len(dataIN)
    i = 0
    while (i < length_dataIN):
        if i % 8 == 0 and i != 0:
            binary += chr(__binary_to_int(octet))
            octet = ""
        octet += dataIN[i]
        i += 1
    return (binary + chr(__binary_to_int(octet)), 8 - len(octet))


def compress(dataIn):
    """
    The main function that makes the whole compression process.
    """

    frequency = buildfrequencylist(dataIn)
    B = buildHuffmantree(frequency)
    E = encodedata(B, dataIn)
    T = encodetree(B)
    
    return (tobinary(E), tobinary(T))

    
################################################################################
## DECOMPRESSION

def __buildEncodeListReverse(encodeList):
    encodeListReverse = {}

    for e in encodeList:
        encodeListReverse[encodeList[e]] = e
    return encodeListReverse


def decodedata(huffmanTree, dataIN):
    """
    Decode a string using the corresponding huffman tree into something more readable.
    """
    encodeList = __huffmanTreeToEncodeData(huffmanTree, "", {})
    encodeListReverse = __buildEncodeListReverse(encodeList)

    length_dataIN = len(dataIN)
    i = 0
    group = ""
    result = ""

    while (i < length_dataIN):
        if (group in encodeListReverse):
            while ((group + dataIN[i]) in encodeListReverse):
                group += dataIN[i]
                i += 1
            i -= 1
            result += encodeListReverse[group]
            group = ""
        else:
            group += dataIN[i]
        i += 1
    return (result + encodeListReverse[group])

def __decodetree_rec(data, i):
    if (data[i] == '1'):
        octet  = ""
        for i in range(i+1, i+9):
            octet += data[i]
        return (bintree.BinTree(chr(__binary_to_int(octet)), None, None), i)
    if (data[i] == '0'):
        leftcall = __decodetree_rec(data, i + 1)
        rightcall = __decodetree_rec(data, leftcall[1] + 1)
        return (bintree.BinTree(None, leftcall[0], rightcall[0]), rightcall[1])

def decodetree(dataIN):
    """
    Decodes a huffman tree from its binary representation:
        * a '0' means we add a new internal node and go to its left node
        * a '1' means the next 8 values are the encoded character of the current leaf         
    """
    return __decodetree_rec(dataIN, 0)[0]


def frombinary(dataIN, align):
    """
    Retrieve a string containing binary code from its real binary value (inverse of :func:`toBinary`).
    """
    length_dataIN = len(dataIN)
    i = 1
    result = ""
    for c in dataIN:
        if (i == length_dataIN):
            result += __removebits(__encodeIn8bits(__dec2bin(ord(c))), align)
        else:
            result += __encodeIn8bits(__dec2bin(ord(c)))
        i += 1
    return result


def decompress(data, dataAlign, tree, treeAlign):
    """
    The whole decompression process.
    """
    encData = frombinary(data, dataAlign)
    encTree = frombinary(tree, treeAlign)

    return decodedata(decodetree(encTree), encData)