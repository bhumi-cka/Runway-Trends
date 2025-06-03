from fashion_clip.fashion_clip import FashionCLIP
from PIL import Image
import torch

fclip = FashionCLIP('fashion-clip')

def get_similarities(image_path, labels):

    image = Image.open(image_path)

    
    text_features = fclip.encode_text(labels, batch_size=1)
    image_features = fclip.encode_images([image], batch_size=1)

    image_features = torch.tensor(fclip.encode_images([image], batch_size=1)).to(torch.float32)
    text_features = torch.tensor(fclip.encode_text(labels, batch_size=1)).to(torch.float32)


    similarities = (image_features @ text_features.T)[0]

    return similarities