import os
from PIL import Image
import requests
import torch
from transformers import CLIPProcessor, CLIPModel

from similarities import get_similarities

labels1={'components':['dress','skirt','top','shirt','jacket'], 'color':['green', 'black', 'brown', 'burgundy', 'red', 'yellow', 'pink', 'blue'], 'print':['animal print', 'floral print', 'geometric print', 'striped print', 'camouflage print', 'abstract print'], 'style':['structured', 'flowy', 'oversized', 'ballgown'], 'length':['maxi', 'midi', 'mini'], 'waistline':['dropped waistline','empire waistline'], 'fabric':['leather', 'denim', 'lace', 'fur', 'sheer', 'fur', 'metallic']}
labels=[]

for component in labels1['components']:
    labels.append(component)
    for key in labels1:
        if key!='components' and key!='length':
            li=labels1[key]
            for item in li:
                labels.append(item + f' {component}')

for comp in ['dress','skirt']:
    for l in ['mini','maxi','midi']:
        labels.append(f'{l} {comp}')



designers=['YSL']
seasons=['Fall Winter']
years=['2025']
shows=['Paris']
all_features={}
for designer in designers:
    for season in seasons:
        for year in years:
            for show in shows:
                dir_path=f"C:/Users/LENOVO/Documents/Runway Predictions/img/{designer} {season} {year} {show}"
                lst=os.listdir(dir_path)
                num_img=len(lst)
                for i in range(1, 3):
                    image_path = f"{dir_path}/img ({i}).jpg"
                    image = Image.open(image_path)
                    
                    similarities = get_similarities(image_path, labels)
                    feature_similarity={}
                    for feature in labels:
                        feature_similarity[feature] = similarities[labels.index(feature)].item()

                    features=[]

                    for feature in feature_similarity:
                        if feature_similarity[feature]>20:
                            features.append(feature)
                    
                    all_features[f'{designer} {season} {year} {show} img ({i})'] = [features]
                        

                                
                    
