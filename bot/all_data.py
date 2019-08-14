# -*- coding: utf-8 -*-
# coding: utf-8
from image_process import process_image_for_ocr
from image_process import get_size_of_scaled_image
from image_process import rotate
from pytesseract import image_to_string
import cv2
from pytesseract import image_to_osd
import re
import sys, json
import pandas as pd
import numpy as np

months =["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre",
         "lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche",
         "jan","fev","sep","oct","nov"]

liste_date_possible=[]
liste_prix_possible=[]
liste_text=[]

restaurant=[]
peage=[]
parking=[]
train=[]
hotel=[]
avion=[]

def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def get_priority():
    d={}
    fiche=pd.read_csv("priority.csv",header=0,delimiter="\t",quoting=2)
    for i in range( len(fiche)):
         d[int(fiche["priority"][i])] = fiche["word"][i]
    dt=sorted(d.items(), key=lambda t: t[0], reverse=False)
    return dt

def get_keys():
    fiche=pd.read_csv("classes.csv",header=0,delimiter="\t",quoting=2)
    for i in range( len(fiche)):
        if fiche["classe"][i] =="restaurant":
            restaurant.append(fiche["key"][i])
        if fiche["classe"][i] =="peage":
            peage.append(fiche["key"][i])
        if fiche["classe"][i] =="parking":
            parking.append(fiche["key"][i])
        if fiche["classe"][i] =="train":
            train.append(fiche["key"][i])
        if fiche["classe"][i] =="hotel":
            hotel.append(fiche["key"][i])
        if fiche["classe"][i] =="avion":
            avion.append(fiche["key"][i])


# 2 motheds to read text in image
def read_image(path):
    config = ('-l fra --oem 1 --psm 3')
    img=process_image_for_ocr(path)
    img=rotate(img)
    text = image_to_string(img, config=config)
    return text

def read_image2(path):
    config = ('-l fra --oem 1 --psm 3')
    img=process_image_for_ocr(path)
    (h, w) = img.shape[:2]
    size=get_size_of_scaled_image(path)
    if (size != (h,w)) :
        rotated_90_clockwise = np.rot90(img)  # rotated 90 deg once
        rotated_180_clockwise = np.rot90(rotated_90_clockwise)
        img = np.rot90(rotated_180_clockwise)
    text = image_to_string(img, config=config)
    return text

def tokenize(string) :
    string = re.sub(r'^-+', '', string)
    string = re.sub(r"'s ", ' ', string)
    string = re.sub(r'\\', '', string)
    string = re.sub(r'[<=>*+\\|]', ' ', string)
    string = re.sub(r'[\[\](){}&#!%?+@€;_\^\"]', '', string)
    string = re.sub(r' +', ' ', string)
    string = re.sub(r'\.+', '.', string)
    string = re.sub(r'\,+', ',', string)
    string = re.sub(r'^ +', '', string)
    string = re.sub(r' +$', '', string)
    string = re.sub(r'—', '', string)
    string = re.sub(r'’', "'", string)
    string = re.sub(r'‘', "'", string)
    string = re.sub(r'”', "'", string)
    string = re.sub(r'“', "'", string)
    string = re.sub(r'^\'+', '', string)
    string = re.sub(r'[\']+$', '', string)
    string = re.sub(r'^-+', '', string)
    string = re.sub(r'[-]+$', '', string)
    return string



def text_to_list(path):
    text=read_image(path) # you can change it with read_image2 if something goes wrong
    l = [tokenize(ch.lower()) for ch in text.split("\n") if ch != '']
    for ch in l :
        if ch !='':
            liste_text.append(ch)


def date_extraction(path):

    l=liste_text
    for ch in l:
        if any([sh in ch for sh in months]):
            liste_date_possible.append(ch)
    if liste_date_possible!=[]:
        return max(liste_date_possible)
    else :
        for ch in l:
            date = re.findall("\d\d[-/]\d\d[-/]\d{2,4}", ch)
            if date != []:
                liste_date_possible.append(date[0])
        if liste_date_possible!=[]:
            return max(liste_date_possible)
        else:
            for ch in l:
                date = re.findall("\d\d[ ]\d\d[ ]\d{2,4}", ch)
                if date != []:
                    liste_date_possible.append(date[0])
            if liste_date_possible != []:
                return max(liste_date_possible)
            else:
                for ch in l :
                    date = re.findall("\d\d[/-]\d\d", ch)
                    if date != []:
                        liste_date_possible.append(date[0])
                if liste_date_possible != []:
                    return max(liste_date_possible)
                else:
                    return "date introuvable"

def price_extraction(path) :
   
    l=liste_text
    d=get_priority()
    for ch in l:
        for t in d :
            if t[1] in ch :
                if re.findall("\d{1,4}[.,-]\d{1,2}", ch)!=[] :
                    for pr in re.findall("\d{1,4}[.,-]\d{1,2}", ch) :
                        liste_prix_possible.append( re.sub(r'[\,-]', '.', pr))
                    break
    if liste_prix_possible!=[] :
        return max(liste_prix_possible)
    else :
        l = [ch for ch in l if all(x not in ch for x in ['tva', 't.v.a.', 'tel', 'km', 'numéro', ])]
        prix_list_prim=[re.findall("\d{1,4}[.,-]\d{1,2}", ch) for ch in l  ]
        for pr in prix_list_prim:
            if pr != []:
                for x in pr:
                    liste_prix_possible.append(x)

        prix_list = [''.join(pr) for pr in liste_prix_possible]
        prix_list = [re.sub(r'[\,-]', '.', ch) for ch in prix_list]
        prix_list = [float(ch) for ch in prix_list if ch.count('.') < 2]
        if prix_list != []:
            return max (prix_list)
        else:
           return "total introuvable"

def classification(path):
   
    l=liste_text
    get_keys()
    r = 0
    p = 0
    pr = 0
    tr = 0
    h=0
    a=0
    for ch in l:
        for indice in restaurant :
            if indice in ch:
                r+=1
    for ch in l:
        for indice in peage:
            if indice in ch:
                p += 1
    for ch in l:
        for indice in parking:
            if indice in ch:
                pr += 1
    for ch in l:
        for indice in train:
            if indice in ch:
                tr += 1
    for ch in l:
        for indice in hotel:
            if indice in ch:
                h += 1
    for ch in l:
        for indice in avion:
            if indice in ch:
                a += 1
    rang=[r,p,pr,tr,h,a]
    type= ["restaurant","peage","parking","train","hotel","avion"]

    if max(rang) !=0 :
        return type[rang.index(max(rang))]
    else:
        return ("type inconnu")



def main():
  url = ''.join(read_in())
  text_to_list(url)
  print ('c est un '+ classification(url)+'\n'+'la date est :' + date_extraction(url)+'\n'+' Total est ' + price_extraction(url))


#start process
if __name__ == '__main__':
    main()



