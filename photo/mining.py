#Processing an image of a table to get data from it
#https://stackoverflow.com/questions/27969091/processing-an-image-of-a-table-to-get-data-from-it

import cv2
import numpy as np
import os

# the list of images (tables)
images = ['table1.png', 'table2.png', 'table3.png', 'table4.png', 'table5.png']

# the list of templates (used for template matching)
templates = ['train1.png']

def remove_duplicates(lines):
    # remove duplicate lines (lines within 10 pixels of eachother)
    for x1, y1, x2, y2 in lines:
        for index, (x3, y3, x4, y4) in enumerate(lines):
            if y1 == y2 and y3 == y4:
                diff = abs(y1-y3)
            elif x1 == x2 and x3 == x4:
                diff = abs(x1-x3)
            else:
                diff = 0
            if diff < 10 and diff is not 0:
                del lines[index]
    return lines


def sort_line_list(lines):
    # sort lines into horizontal and vertical
    vertical = []
    horizontal = []
    for line in lines:
        if line[0] == line[2]:
            vertical.append(line)
        elif line[1] == line[3]:
            horizontal.append(line)
    vertical.sort()
    horizontal.sort(key=lambda x: x[1])
    return horizontal, vertical


def hough_transform_p(image, template, tableCnt):
    # open and process images
    img = cv2.imread('imgs/'+image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # probabilistic hough transform
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 200, minLineLength=20, maxLineGap=999)[0].tolist()

    # remove duplicates
    lines = remove_duplicates(lines)

    # draw image
    for x1, y1, x2, y2 in lines:
        cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 1)

    # sort lines into vertical & horizontal lists
    horizontal, vertical = sort_line_list(lines)

    # go through each horizontal line (aka row)
    rows = []
    for i, h in enumerate(horizontal):
        if i < len(horizontal)-1:
            row = []
            for j, v in enumerate(vertical):
                if i < len(horizontal)-1 and j < len(vertical)-1:
                    # every cell before last cell
                    # get width & height
                    width = horizontal[i+1][1] - h[1]
                    height = vertical[j+1][0] - v[0]

                else:
                    # last cell, width = cell start to end of image
                    # get width & height
                    width = tW
                    height = tH
                tW = width
                tH = height

                # get roi (region of interest) to find an x
                roi = img[h[1]:h[1]+width, v[0]:v[0]+height]

                # save image (for testing)
                dir = 'imgs/table%s' % (tableCnt+1)
                if not os.path.exists(dir):
                     os.makedirs(dir)
                fn = '%s/roi_r%s-c%s.png' % (dir, i, j)
                cv2.imwrite(fn, roi)

                # if roi contains an x, add x to array, else add _
                roi_gry = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                ret, thresh = cv2.threshold(roi_gry, 127, 255, 0)
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                if len(contours) > 1:
                    # there is an x for 2 or more contours
                    row.append('x')
                else:
                    # there is no x when len(contours) is <= 1
                    row.append('_')
            row.pop()
            rows.append(row)

    # save image (for testing)
    fn = os.path.splitext(image)[0] + '-hough_p.png'
    cv2.imwrite('imgs/'+fn, img)


def process():
    for i, img in enumerate(images):
        # perform probabilistic hough transform on each image
        hough_transform_p(img, templates[0], i)


if __name__ == '__main__':
    process()