features=[]
feature='skirt'
features_list = feature.split()
if len(features_list) > 1:
    features.append(' '.join(features_list[:-1]))
else:
    features.append(feature)
print(features)  