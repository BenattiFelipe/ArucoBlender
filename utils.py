import cv2
import numpy as np
import math
import os
import matplotlib.pyplot as plt
import pandas as pd
from tabulate import tabulate
from mpl_toolkits.mplot3d import Axes3D
import imutils

def amb3dNovaInformacao(ids,ids_grp,TabAruco3D):
    idsRepitidos, indexIdsRepitidos = foundRepIds(TabAruco3D, ids)
    gruposVerificados=[]
    for i in ids_grp:
        for j in i:
            verificacao=[]
            if j in idsRepitidos:
                verificacao.append(True)
            else:
                verificacao.append(False)
        if any(verificacao):
            gruposVerificados.append(True)
        else:
            gruposVerificados.append(False)
    if all(gruposVerificados):
        return(False)
    return(True)

def amb2dNovaInformacao(ids,ids_rep,ids_grp):
    for i in ids_grp:
        if len(i)>1:
            i=sorted(i)
            ids_rep=sorted(ids_rep)
            conts=0
            for j in i:
                if j in ids_rep:
                    conts=conts+1
            if conts==len(i):
                return True
    return False

def foundCenter(c):
    M = cv2.moments(c)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    center_model_Aruco = [cX, cY]
    return center_model_Aruco

def foundRepIds(Tab1,ids):
    ids_rep = []
    index_rep = []
    for i in range(len(Tab1) - 1, -1, -1):
        t = list(Tab1.loc[i])
        if t[1] in ids:
            ids_rep.append(t[1])
            index_rep.append(i)
    return (ids_rep,index_rep)

def criaDic(corners, ids, pts_real_Aruco):
    dictID={}
    for (markerCorner, markerID) in zip(corners, ids):
        c = markerCorner[0]
        try:
            csort = sortCorners(c)
            carray = np.float32(csort.copy())
        except ValueError:
            print("CSORT:",csort)
        matriz, mask = cv2.findHomography(carray, pts_real_Aruco,0)
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        center_model_Aruco=[cX,cY]

        dictID.update({markerID: [center_model_Aruco, matriz, c]})
    return dictID

def sortCorners(corners):
    minx = miny = 10000000
    maxy = 0
    bol1=False
    outros=[]
    minxv = [[]]
    maxxv = []
    new_corners = []
    for i in corners:
      if i[0]<minx:
        if len(minxv)<2 and bol1:
          outros.append(minxv[0])
        elif bol1:
          outros.append(minxv[0])
          outros.append(minxv[1])
        minx=i[0]
        minxv = [[]]
        minxv[0]=i.copy()
        bol1=True
      elif i[0]==minx:
        minxv.append(i)
      else:
        outros.append(i)

    if len(minxv)==2:
      if minxv[0][1]>minxv[1][1]:
        p1 = minxv[1]
        p4 = minxv[0]
      else:
        p1 = minxv[0]
        p4 = minxv[1]
      if outros[0][1]>outros[1][1]:
        p2 = outros[1]
        p3 = outros[0]
      else:
        p2 = outros[0]
        p3 = outros[1]
    else:
      outros2=[]
      minx = miny = 10000000
      px = minxv[0].copy()
      minxv=[[]]
      bol2=False
      for i in outros:
        if i[0]<minx:
          if len(minxv)<2 and bol2:
            outros2.append(minxv[0])
          elif bol2:
            outros2.append(minxv[0])
            outros2.append(minxv[1])
          minx=i[0]
          minxv = [[]]
          minxv[0]=i.copy()
          bol2=True
        elif i[0]==minx:
          minxv.append(i)
        else:
          outros2.append(i)
      if len(minxv)==2:
        if minxv[0][1]>minxv[1][1]:
          p2 = minxv[1]
          p4 = minxv[0]
        else:
          p2 = minxv[0]
          p4 = minxv[1]
        p3=outros2[0].copy()
      else:
        pxx=minxv[0].copy()
        if px[1]<pxx[1]:
          p1=px.copy()
          p4=pxx.copy()
        else:
          p1=pxx.copy()
          p4=px.copy()

        if outros2[0][1]>outros2[1][1]:
          p2 = outros2[1]
          p3 = outros2[0]
        else:
          p2 = outros2[0]
          p3 = outros2[1]

    new_corners=[p1,p2,p3,p4]
    return (new_corners)

def enquadraFrame(img,corners):
    miny=img.shape[1]
    minx=img.shape[0]
    maxy=0
    maxx=0
    for i in corners:
        for j in i[0]:
            miny=min(miny,j[1])
            minx = min(minx, j[0])
            maxy=max(maxy, j[1])
            maxx=max(maxx, j[0])
    x1 = int(minx - 20)
    x2 = int(maxx + 20)
    y1 = int(miny - 20)
    y2 = int(maxy + 20)

    return img[y1:y2 , x1:x2]

def fakeWrap(matriz,pt):
    x=pt[0]
    y=pt[1]
    d1=(matriz[0][0]*x+matriz[0][1]*y+matriz[0][2])/(matriz[2][0]*x+matriz[2][1]*y+matriz[2][2])
    d2 = (matriz[1][0] * x + matriz[1][1] * y + matriz[1][2]) / (matriz[2][0] * x + matriz[2][1] * y + matriz[2][2])
    return [d1,d2]

def idsDiferentes(ids,ids_ant):
    novo=[]
    if len(ids_ant)==0:
        return ids
    for i in range(len(ids)):
        if ids[i] not in ids_ant:
            novo.append(ids[i])
    return novo

def criarGrupos(n_grp):
    grp=[]
    for i in range(0,n_grp):
        grp.append([])
        for j in range(10):
            grp[i].append((i+1)*10+j)
    return grp

def qntPlanos(ids,grp):
    in_grp=[]
    cont_planos=0
    for i in grp:
        cont=0
        den=[]
        for j in ids:
            if j in i:
                cont=cont+1
                den.append(j)
        if cont>0:
            in_grp.append(den)
    return len(in_grp),in_grp

def find_aruco(img, dict_aruco = cv2.aruco.DICT_6X6_250):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    aruco_dict = cv2.aruco.Dictionary_get(dict_aruco)
    parameters = cv2.aruco.DetectorParameters_create()
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    return corners, ids

def distanc(p1,p2):
  dist= np.sqrt(((p1[0]-p2[0])**2) + ((p1[1]-p2[1])**2))
  return dist

def calcula_area(quatro_pontos):
    pda, pab, pbc, pcd = quatro_pontos
    a = distanc(pda, pab)
    b = distanc(pab, pbc)
    c = distanc(pbc, pcd)
    d = distanc(pcd, pda)
    e = distanc(pab, pcd)
    p1 = (a + d + e) / 2
    p2 = (b + c + e) / 2
    A1 = np.sqrt(p1 * (p1 - a) * (p1 - d) * (p1 - e))
    A2 = np.sqrt(p2 * (p2 - b) * (p2 - c) * (p2 - e))
    A = A1 + A2
    return A

def verificaArea(quatro_pontos, ref, error):
  Area = calcula_area(quatro_pontos)
  if math.fabs(Area-ref)<error:
      return True
  else:
      return False

def fakeWarpCorners(corners,matriz):
    new_c=[]
    for i in corners:
        new_c.append(fakeWrap(matriz,i))
    return new_c

def achaGrupoPrincipal(TabAruco3D):
    ids=[]
    grp = criarGrupos(5)
    for p in range(len(TabAruco3D)):
        rol = TabAruco3D.loc[p]
        id = rol.get("ArucoID")
        ids.append(id)
    numPlanos, ids_grp = qntPlanos(ids, grp)
    maiorgrp=[]
    for i in range(len(ids_grp)):
        if len(ids_grp[i])>len(maiorgrp):
            maiorgrp=ids_grp[i].copy()
    grupoPrincipal= (maiorgrp[0]//10)*10
    return grupoPrincipal
