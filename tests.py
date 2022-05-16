import cv2
from utils import *
import imutils

import cv2
import numpy as np

def calcula_erro_identidade(info_dic):
    matriz_H = info_dic[1]
    center = info_dic[0]
    pt = fakeWrap(matriz_H,center)
    error = [abs(pt[0]),abs(pt[1])]
    return error

def detect_areas(img, area_min=0):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	blur = cv2.medianBlur(gray, 5)
	sharpen_kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
	sharpen = cv2.filter2D(blur, -1, sharpen_kernel)

	# Threshold and morph close
	thresh = cv2.threshold(sharpen, 0, 100, cv2.THRESH_BINARY_INV)[1]
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
	close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

	# Find contours and filter using threshold area
	cnts = cv2.findContours(close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	# cnts = cnts[0] if len(cnts) == 2 else cnts[1]
	min_area = area_min
	max_area = 300000
	image_number = 0
	for c in cnts:
		area = cv2.contourArea(c)
		if area > min_area and area < max_area:
			x,y,w,h = cv2.boundingRect(c)
			ROI = image[y:y+h, x:x+w]
			cv2.imwrite('ROI_{}.png'.format(image_number), ROI)
			cv2.rectangle(image, (x, y), (x + w, y + h), (0,0,255), 3)
			image_number += 1


	# cv2.imshow('sharpen', sharpen)
	# cv2.imshow('close', close)
	# cv2.imshow('thresh', thresh)
	# cv2.imshow('image', image)
	# cv2.waitKey()
	# cv2.destroyAllWindows()

	return(area, [[x, y], [x+w, y], [x, y+h], [x + w, y + h]])

def pontos_iniciais(largura, altura):
	return(np.float32([[largura/2, altura/2], [-largura/2, altura/2], [-largura/2, -altura/2], [largura/2, -altura/2]]))

def poly_area(c):
  add = []
  for i in range(0, (len(c) - 2), 2):
    add.append(c[i] * c[i + 3] - c[i + 1] * c[i + 2])
    add.append(c[len(c) - 2] * c[1] - c[len(c) - 1] * c[0])
    return abs(sum(add) / 2)

def polygon_area(x,y):
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))



path = 'video/scale/'
EI = []
EP = []
EA = []

for i in range (1,32) :
	print("imagem:",path+"scale_"+str(i)+'.PNG')
	img = cv2.imread(path+"scale_"+str(i)+'.PNG')
	img = imutils.resize(img, width=600)
	image = img.copy()

	corners, ids = find_aruco(img)
	cv2.aruco.drawDetectedMarkers(img, corners, ids)
	pt = pontos_iniciais(0.15,0.15)
	pt = sortCorners(pt)
	pt = np.float32(pt)
	dic = criaDic(corners, ids.flatten(), pt)
	H = dic[42][1]
	H_inv = np.linalg.inv(H)
	erro = calcula_erro_identidade(dic[42])
	areas, corners_area = detect_areas(img, 1000)
	c_area_real = fakeWarpCorners(corners_area, H)
	c_real = pontos_iniciais(0.2, 0.2)
	c_real = sortCorners(c_real)
	ep = np.sum(np.abs(np.array(c_area_real) - c_real))
	x = []
	y = []
	for a in c_area_real:
		x.append(a[0])
		y.append(a[1])
	area = calcula_area(c_area_real)#poly_area(c)
	area_real = (i*0.01+0.2)**2
	ea = abs(area_real - area)
	EI.append(erro)
	EA.append(ea)
	EP.append(ep)

#Plot error
import matplotlib.pyplot as plt
# plt.plot(EI, label='Erro identidade')
plt.plot(EA, label='Erro area')
plt.plot(EP, label='Erro pontos')
plt.legend()
plt.show()

# cv2.imshow('img',img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()