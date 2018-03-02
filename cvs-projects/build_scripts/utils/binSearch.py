#!/usr/bin/python


#This script will attempt to construct a binary search tree we can use for fast searching
#(i.e. we load a file into this bst and look through this tree instead of a linear search)


#a node, its bst, you can go left right, or just look at what we have.
#this can be generic, but the search functions will have to be speficic to the
#datatype we're going to search for.

#thank the python cookbook for the majority of this code: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/286239

#no clean up routines cause we'll let python and the os do that for us.

#dataObject is the class we'll use to organize parsed data from the file
#its easier to pass around this object than a buncha variables (yea, we coulda used a tuple/list)
class fileData:
  def __init__(self):
    self.buildTag  = None  #necessary element here, gonna use for searching
    self.startDate = None
    self.expDate   = None
    self.emailAddr = None

#trying some weird stuff to get around the pointer issue
#We can't just store the object since python will copy the address of the original variable
#we copy the immutable objects and things are happy
class TreeNode:
  def __init__(self, nodeData):
    self.left = None
    self.right = None
    self.bTag = nodeData.buildTag
    self.start = nodeData.startDate
    self.date = nodeData.expDate
    self.email = nodeData.emailAddr
    self.done = 0 #build tags exist in multiple places, this is to avoid
		  #having several emails
#Our tree, our methods for the tree
class Tree:

  def __init__(self):
    self.root = None

  #assigns the data to a new TreeNode
  def addNode(self, inputData):
    return TreeNode(inputData)  #insert is recursive, so when it reaches its ending point this is called

  #this function traverses the tree and finds the spot to add the node
  def insertNode(self, inputData, root):

#We don't need this part anymore, we check for empty nodes before visiting them now
#the original code basically reconstructed the tree on every entry, we're trying to avoid
#this by changing how it works from the code taken from the website


#    if root == None:
#      return self.addNode(inputData)
#    else:

#leaving the original code in tact for historical purposes
      if inputData.buildTag <= root.bTag:
#        root.left = self.insertNode(inputData, root.left)  #original way of doing this, inefficient
        if root.left == None:
          root.left = self.addNode(inputData) #left is empty? add
        else:
          self.insertNode(inputData, root.left) #visit the left subtree

      else:
#        root.right = self.insertNode(inputData, root.right)
        if root.right == None:
          root.right = self.addNode(inputData)
        else:
          self.insertNode(inputData, root.right) 
      return #root

  def findNode(self, nodeToFind, root): #nodeToFind is just a buildTag string
    if root == None:
      return None
    else:
      #print "Comparing " + nodeToFind + " and " + root.bTag
      if nodeToFind == root.bTag:
        return root
      elif nodeToFind < root.bTag:
        return( self.findNode(nodeToFind, root.left) )
      else:
        return( self.findNode(nodeToFind, root.right) ) 



