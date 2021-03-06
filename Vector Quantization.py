# -*- coding: utf-8 -*-
"""Yifan Lou CMSC422 Problem Set 3

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sgy_D7aq-G_0JHRm_UZmX8BB6mA9BlhW

# Problem Set 3: Using K-means Clustering for Vector Quantization
# CMSC 422, Fall 2020
# Due Oct 15 at 3:30pm

<center>
<img src="https://drive.google.com/thumbnail?id=1D7Byd2RlUqm5sAq0jxl6yzkGtuSJ3YK4&sz=w1000" alt="meme"/>
</center>

## Submission Instructions

**Once** you have completed the problems, download this Colab notebook **as a notebook file** by navigating to `File > Download .ipynb`, and submit it on Gradescope. This assignment will be autograded so follow instructions closely.  __Note:__ Using anything other then `matplotlib` for your plots may crash the autograder. Also, make sure none of your code cells are throwing exceptions.

## Overview
This problem set focuses on K-means clustering.  This algorithm is described in Section 3.4 of Daume's book, with an improved version and some theoretical results given in Section 15.1.  We are given vectors in a high-dimensional space. Our goal is to identify k cluster centers and an assignment of vectors, one to each cluster, that minimizes the sum of squared distance from the vectors to their corresponding cluster centers.

We illustrate this using an important application of clustering to vector quantization.  We will experiment with this in the context of images.  An image consists of pixels.  Each pixel has a red, green and blue value, which are typically represented with 8 bit unsigned integers.  This means every color has a value between 0 and 255.  If we represent these values explicitly, we need 24 bits for every pixel in the image.  If our image has N pixels, we need 24N bits.

But suppose our image only contained 256 distinct colors.  In that case, we could represent the image with much less space.  We would just need a table of 256 colors.  Then, for every pixel we could describe its color with an index into this table.  Representing such a table requires 256*24 bits, while representing the indices requires 8N bits.  Since N is typically very large (megapixel cameras are ubiquitous), we would reduce the size of our image by about a factor of 3.

But real images don't have 256 different colors, they may have millions of different colors.  But many of these colors are pretty similar, so we can often approximate an image with a small number of colors.  We want to do this with as little distortion of the true colors as possible.  K-means is perfect for this.  The cluster centers will be the colors we put in the table.  The assignment of pixels to cluster centers will tell us what color to use in the approximate image for each pixel.  And the objective function of K-means is a way of saying we want to find the colors for the table and a way of assigning pixels to these colors that minimizes the distortion of the image.

## Getting started with images

We begin by importing some standard libs.  cv2 is OpenCV, a standard library used for computer vision.
"""

import cv2
import os
import numpy as np
from matplotlib import pyplot as plt
from google.colab import drive

"""Click on the links below and download the images we will be working with:
- [peppers.jpg](https://drive.google.com/file/d/1aN2c8mp72qCrQn7_3CecCv9HgzpqAc82/view?usp=sharing)
- [peppers_small.jpg](https://drive.google.com/file/d/143lBsMzNjLJAagaeva6Zooj2OpT1I0bG/view?usp=sharing)

Next, this code allows you to select a file to load on your computer.  Use it to load the two images you have downloaded, peppers.jpg and peppers_small.jpg.  We suggest that you do all experiments with peppers_small.jpg.  When everything is working you can run with peppers.jpg to see how things look.
"""

from google.colab import files
uploaded = files.upload()  # (you can select more than one file)

"""The next code reads the images into Python, and shows how to display them."""

imgsmall = cv2.imread('peppers_small.jpg')
img = cv2.imread('maxresdefault.jpg')

from google.colab.patches import cv2_imshow
cv2_imshow(img)
cv2_imshow(imgsmall)

"""Each image is a 3D array.  For every (x,y) position there is a pixel, and every pixel contains three values.  These are RGB values (red, green, blue), which say how much of each color is in a pixel."""

x,y,z = imgsmall.shape

[x,y,z]

"""See, the small image has 77 rows and 103 columns, and 3 values for each pixel.  We can access a pixel value just by indexing into it.  For example:"""

[img[0,0,0], img[0,0,1], img[0,0,2]]

"""The pixel in the upper left corner is kind of purple.  It's dark, but it has a fair amount of R (red) and B (blue), and less G (green).

## Problem 1 (15 points)

We'll begin by writing code to compute the distance from each pixel to a cluster center.
"""

def cluster_points_distance_squared(cl, img):
  a, b, c = img.shape
  res = []
  for pixel in img:
    for p in pixel:
      distance = 0
      for i in range(len(p)):
        distance += (p[i] - cl[i])**2
      res.append(distance)
  return np.array(res).reshape(a, b)

"""Just to test this, here's the output of our code on a simple problem:"""

testim = np.empty([2,2,3])
testim[0,0,0:3] = [1,0,0]
testim[0,1,0:3] = [0,1,0]
testim[1,0,0:3] = [0,0,1]
testim[1,1,0:3] = [1,1,1]
cl = np.array([1,0,1])
cluster_points_distance_squared(cl, testim)

"""The output looks like:  
array([[1., 3.],
       [1., 1.]])

## Problem 2 (15 Points)

Now, implement a function to decide what cluster each pixel belongs to.  You'll compute the distance from each cluster center to each pixel, and assign each pixel to the nearest cluster.  One corner case that can arise is when a pixel is equidistant to two or more cluster centers.  This can be handled in a variety of ways.  Normally, it's not too important how you deal with this.  But to make it easier for us to test your code, we will require that such a pixel be assigned to the cluster that comes first in the list, cls, which is input to the function.
"""

def cluster_members(cls, img):
  a, b, c = img.shape
  res = []
  for pixel in img:
    for p in pixel:
      dis = getDistance(cls, p)
      newcls = np.argsort(dis)
      res.append(newcls[0])
  return np.array(res).reshape(a, b)

def getDistance(cls, p):
  dis = []
  for cl in cls:
    distance = 0;
    for i in range(len(p)):
        distance += (p[i] - cl[i])**2
    dis.append(distance)
  return dis

"""Ok, just to check this, we run on a simple test case.  """

testim = np.empty([2,2,3])
testim[0,0,0:3] = [1,1,0]
testim[0,1,0:3] = [0,1,0]
testim[1,0,0:3] = [0,1,1]
testim[1,1,0:3] = [0,0,1]
cl0 = np.array([.3,.8,0])
cl1 = np.array([0, .1, .8])
cls = [cl0, cl1]
cls[1]
asgn = cluster_members(cls, testim)
asgn

"""The result of running this code is:

array([[0, 0],
       [1, 1]])

## Problem 3 (20 Points)

Next, write a function that will update the centers of the clusters, based on cluster assignments that have been computed. Each cluster center should be updated to be the average of the pixels assigned to that center.

Note that it is possible that a cluster will contain no pixels.  That is ok, but must be handled without your code blowing up.  One might deal with this issue in a few different ways.  For simplicity, in your code, just assign the cluster a center of [-255,-255,-255].  This will result in the cluster being out of action, and not having any pixels assigned to it in the future.
"""

def update_centers(asgn, img, k):
  res = []
  for i in range(k):
    a, b = np.where(asgn == i)
    if (len(a) == 0):
      res.append([-255,-255,-255])
    else:
      temp = []
      for x in range(len(a)):
        temp.append(img[a[x], b[x], ])
      y = getNewCenter(temp)
      res.append(y)
  return np.array(res).reshape(k, 3)

def getNewCenter(img):
  return np.array([(sum(column)/len(column)) for column in zip(*img)])

"""Again, we'll try this on a simple example, using the results from the last example:"""

cls = update_centers(asgn, testim, 2)
cls

"""The answer that our code produces is:

[array([0.5, 1. , 0. ]), array([0. , 0.5, 1. ])]

## Problem 4 (10 points)

Now we will put these functions together to perform k-means clustering.  You will define a function that takes as input the initial values of the clusters. We provide a simple initialization method.  This makes it easier to test your code.

Also, in k-means one might test to see if the algorithm has converged.  However, to keep things simple, we will just ask you to iterate a fixed number of times, so you don't need to bother testing.
"""

def initialized_k_means(cls, img, n):
  a = len(cls)
  res = []
  for i in range(n):
    asgn = cluster_members(cls, img)
    cls = update_centers(asgn, img, a)
  for c in cls:
    res.append(c)
  return res, asgn

"""Ok, a simple example:"""

testim = np.empty([2,2,3])
testim[0,0,0:3] = [0,0,0]
testim[0,1,0:3] = [2,0,0]
testim[1,0,0:3] = [6,0,0]
testim[1,1,0:3] = [8,0,0]
cl0 = np.array([1,0,0])
cl1 = np.array([8, 6, 0])
cls = [cl0, cl1]
cls1, asgn1 = initialized_k_means(cls, testim, 1)
print(cls1)
print(asgn1)
cls2, asgn2 = initialized_k_means(cls, testim, 2)
print(cls2)
print(asgn2)

"""The result of our code is:

[array([2.66666667, 0.        , 0.        ]), array([8., 0., 0.])]
[[0 0]
 [0 1]]
[array([1., 0., 0.]), array([7., 0., 0.])]
[[0 0]
 [1 1]]

## Problem 5 (25 Points)

Ok, we are now ready to quantize an image.  We will provide a baseline function to initialize the cluster centers, and a function to measure how close the quantized image is from the original image, to allow evaluation.
"""

###########################
# DO NOT MODIFY THIS CELL #
###########################

def simple_init(k):
  # Function will return a list of k classes.
  # Note that rgb values are between 0 and 255.
  np.random.seed(42)
  cls = [];
  for i in range(k):
    cls += [np.random.randint(0,256,3)]
  return cls

def compare_images(img1, img2):
  return np.sqrt(np.sum((img1-img2)**2))

def quantize_image(img, k, n):
  # This takes an image, img, a number of cluster, k, and a number of iterations, n.
  # k should be the cube of an integer (eg., 8, 27, 64, ....)
  # It returns a new image.  The new image should have only k unique clusters.
  # It also returns a list of the cluster centers. Like before, return them as 
  # a tuple.
  # ADD YOUR CODE BELOW
  newimg = []
  cls = simple_init(k)
  cluster, asgn = initialized_k_means(cls, img, n)
  newcls = np.array(cluster)
  for asg in asgn:
     newimg.append(newcls[asg])
  return np.array(newimg).reshape(img.shape), newcls

"""Now we can run this code on a real image.  We can see that when we use 128 colors, we get something that looks pretty similar to the original image.  With 8 colors, there are noticeable artifacts, but we have a comprehensible image.  This might be useful for very compact thumbnails."""

qimgsmall8, cls8 = quantize_image(imgsmall, 8, 10)
# qimgsmall256, cls256 = quantize_image(imgsmall, 256, 10)
cv2_imshow(imgsmall) 
cv2_imshow(qimgsmall8)
# cv2_imshow(qimgsmall256)
print(compare_images(imgsmall, qimgsmall8))
# print(compare_images(imgsmall, qimgsmall256))

"""We can look at this on the full-sized image too, though this is going to take a lot longer to run (took me around 30 minutes)."""

qimg8, cls8 = quantize_image(img, 64, 10)
#qimg128, cls128 = quantize_image(img, 128, 10)
cv2_imshow(img) 
cv2_imshow(qimg8)
#cv2_imshow(qimg128)
print(compare_images(img, qimg8))
#print(compare_images(img, qimg128))

"""## Problem 6 (15 Points)

Finally, the last problem is to find a way to improve on these results.  That is, you need to find a way to improve k-means so that it produces a better image, using the same number of clusters (that is, you shouldn't improve the result by just increasing k).

Your improvements should not be specific to the pepper image.  We will test your code on three new images.  To get full credit, your result must be better on all three than the code we write as the answer to Problem 5.  One way of doing this is suggested in the text by Daume.
"""

def better_quantize_image(img, k, n):
  newimg = []
  cls = initial_cls(img, k)
  cluster, asgn = initialized_k_means(cls, img, n)
  newcls = np.array(cluster)
  for asg in asgn:
     newimg.append(newcls[asg])
  return np.array(newimg).reshape(img.shape), newcls

def initial_cls(img, k):
  cls = []
  a, b, c = img.shape
  sum_dis = 0
  cls.append(img[np.random.randint(0, a), np.random.randint(0, b)])
  for i in range(1, k):
    next_cls = None
    max_dis = np.iinfo(np.int16).min
    for pixel in img:
      for p in pixel:
        dis = get_Distance(cls, p)
        if dis > max_dis:
          max_dis = dis
          next_cls = p
    cls.append(next_cls)
    
  return np.array(cls)

def get_Distance(cls, p):
  mindis = np.iinfo(np.int16).max
  for cl in cls:
    distance = 0;
    for i in range(len(p)):
      distance += (p[i] - cl[i])**2
    distance = distance**(1/2)
    if distance < mindis:
      mindis = distance
  return mindis

"""Here is an example showing our codes performance"""

qimgsmall1, cls1 = quantize_image(imgsmall, 16, 10)
qimgsmall2, cls2 = better_quantize_image(imgsmall, 16, 10)
cv2_imshow(imgsmall) 
cv2_imshow(qimgsmall1)
cv2_imshow(qimgsmall2)
print(compare_images(imgsmall, qimgsmall1))
print(compare_images(imgsmall, qimgsmall2))