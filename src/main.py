import sys
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt


def load_config(filename: string):
  colors = []
  brightness_ampl = []
  radius_ampl = []
  
  with open(filename, 'r') as f:
    text = f.read().split('-\n')

  group = [g.strip().split('\n') for g in text]

  colors = [[int(hex[i:i+2], 16) for i in (0, 2, 4)] for hex in group[0]]
  for col in colors:
    col.reverse() # going to bgr
    
  colors = cv.cvtColor(np.uint8([colors]), cv.COLOR_BGR2HSV)[0] # going to hsv

  hue_ampl = [int(num) for num in group[1][0].split(' ')]
  sat_ampl = [int(num) for num in group[2][0].split(' ')]
  value_ampl = [int(num) for num in group[3][0].split(' ')]
  radius_ampl = [int(num) for num in group[4][0].split(' ')]

  return colors, hue_ampl, sat_ampl, value_ampl, radius_ampl


def main():
  if len(sys.argv) < 2:
    print('Please, specify input image path.')
    return
  
  colors, hue_ampl, sat_ampl, value_ampl, radius_ampl = load_config('config.txt')

  print('colors: ', colors)
  print('value_ampl: ', value_ampl)
  print('radius_ampl: ', radius_ampl)

  img = cv.imread(sys.argv[1], cv.IMREAD_COLOR)
  img = cv.cvtColor(img, cv.COLOR_BGR2HSV)
  
  filtered = []
  
  for col in colors:
    lower = col + np.int8([hue_ampl[0], sat_ampl[0], value_ampl[0]])
    upper = col + np.int8([hue_ampl[1], sat_ampl[1], value_ampl[1]])
    
    mask = cv.inRange(img, lower, upper)
    
    filtered.append(mask)
  
  print(len(filtered[0]))

  concat = cv.vconcat([ cv.hconcat([filtered[i], filtered[i+1]]) for i in [0, 2] ])
  
  window_name = "opencv"
  cv.namedWindow(window_name, cv.WINDOW_AUTOSIZE)
  cv.imshow(window_name, concat)

  while True:
    c = cv.waitKey(500)

    if c == 27 or c == 113:
        break
        
if __name__ == '__main__':
  main()
