import sys
import re
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

# usage:
#
# python src/main.py config1.txt assets/1.jpg
# python src/main.py config2.txt assets/6.jpg

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


def show_gabarito(filename: string, r, g, b, y):
  matches = re.findall(r'-?\d*\.?\d+', filename)
  imgnum = int(matches[0])
  
  with open('gabarito.txt', 'r') as f:
    gabarito = f.read().split('\n')

  started = 0
  for line in gabarito:
    line = line.strip()
    if started > 0:
      if line.startswith('Imagem'):
        break;
      elif line.startswith('Vermelho'):
        total = line.split(' ')[-1]
        print(f'Vermelho: {r}/{total}')
      elif line.startswith('Amarelo'):
        total = line.split(' ')[-1]
        print(f'Amarelo: {y}/{total}')
      elif line.startswith('Verde'):
        total = line.split(' ')[-1]
        print(f'Verde: {g}/{total}')
      elif line.startswith('Azul'):
        total = line.split(' ')[-1]
        print(f'Azul: {b}/{total}')
        
    if line.startswith(f'Imagem {imgnum}:'):
      started = 1

def main():
  if len(sys.argv) < 3:
    print('Please, specify config and input image paths.')
    return
  
  colors, hue_ampl, sat_ampl, value_ampl, radius_ampl = load_config(sys.argv[1])

  print('colors: ', colors)
  print('value_ampl: ', value_ampl)
  print('radius_ampl: ', radius_ampl)

  img = cv.imread(sys.argv[2], cv.IMREAD_COLOR)
  img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
  
  masks = []
  circles = []
  final = img.copy()
  
  count = [0, 0, 0, 0]
  
  for i, col in enumerate(colors):
    col = np.array(col, dtype=int)
    lower = np.clip(col + [hue_ampl[0], sat_ampl[0], value_ampl[0]], 0, [179, 255, 255]).astype(np.uint8)
    upper = np.clip(col + [hue_ampl[1], sat_ampl[1], value_ampl[1]], 0, [179, 255, 255]).astype(np.uint8)
    
    # print(f'lower: {lower}\n upper: {upper}')
    
    mask = cv.inRange(img_hsv, lower, upper)
    mask = cv.GaussianBlur(mask, (5, 5), 0)
    
    hcircles = cv.HoughCircles(mask, cv.HOUGH_GRADIENT, 1.0, 40,
                               param1=50,param2=17, minRadius=radius_ampl[0], maxRadius=radius_ampl[1])
    
    output = img.copy()
    
    hcircles = np.uint16([[]]) if hcircles is None \
               else np.uint16(np.around(hcircles))
    
    for circle in hcircles[0,:]:
      count[i] += 1
      
      cv.circle(output, (circle[0], circle[1]), circle[2], (0, 255, 0), 2)
      cv.circle(output, (circle[0], circle[1]), 2, (0, 0, 255), 3)
      
      rgb_col = cv.cvtColor(np.uint8([[[col[0], 255, 255]]]), cv.COLOR_HSV2BGR)[0][0].tolist()
      
      cv.circle(final, (circle[0], circle[1]), circle[2],  rgb_col , 2)
      cv.circle(final, (circle[0], circle[1]), 2, (0, 0, 0), 7)
      cv.circle(final, (circle[0], circle[1]), 2, rgb_col, 5)
    
    masks.append(cv.cvtColor(mask, cv.COLOR_GRAY2BGR))
    circles.append(output)
  
  show_gabarito(sys.argv[2], count[3], count[1], count[0], count[2])
  
  # concat = cv.vconcat([ cv.hconcat([masks[i], masks[i+1], circles[i], circles[i+1]]) for i in [0, 2] ])
  concat = final
  
  window_name = "opencv"
  cv.namedWindow(window_name, cv.WINDOW_AUTOSIZE)
  cv.imshow(window_name, concat)

  while True:
    c = cv.waitKey(500)

    if c == 27 or c == 113:
        break
        
if __name__ == '__main__':
  main()
