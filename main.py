import torch
import flask
from flask import Flask, request, render_template
#import joblib
import numpy as np
from scipy import misc
import torch.nn as nn
import torchvision.models as models
from torchvision.datasets import ImageFolder
import torchvision.transforms as transforms
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image
app = Flask(__name__)

transformations = transforms.Compose([transforms.Resize((256, 256)), transforms.ToTensor()])

dataset = ['cardboard', 'glass', 'metal', 'paper', 'plastic', 'trash']

class ImageClassificationBase(nn.Module):
    def training_step(self, batch):
        images, labels = batch 
        out = self(images)                  # Generate predictions
        loss = F.cross_entropy(out, labels) # Calculate loss
        return loss
    
    def validation_step(self, batch): 
        images, labels = batch 
        out = self(images)                    # Generate predictions
        loss = F.cross_entropy(out, labels)   # Calculate loss
        acc = accuracy(out, labels)           # Calculate accuracy
        return {'val_loss': loss.detach(), 'val_acc': acc}
        
    def validation_epoch_end(self, outputs):
        batch_losses = [x['val_loss'] for x in outputs]
        epoch_loss = torch.stack(batch_losses).mean()   # Combine losses
        batch_accs = [x['val_acc'] for x in outputs]
        epoch_acc = torch.stack(batch_accs).mean()      # Combine accuracies
        return {'val_loss': epoch_loss.item(), 'val_acc': epoch_acc.item()}
    
    def epoch_end(self, epoch, result):
        print("Epoch {}: train_loss: {:.4f}, val_loss: {:.4f}, val_acc: {:.4f}".format(
            epoch+1, result['train_loss'], result['val_loss'], result['val_acc']))

class ResNet(ImageClassificationBase):
    def __init__(self):
        super().__init__()
        # Use a pretrained model
        self.network = models.resnet50(pretrained=True)
        # Replace last layer
        num_ftrs = self.network.fc.in_features
        self.network.fc = nn.Linear(num_ftrs, len(dataset))
    
    def forward(self, xb):
        return torch.sigmoid(self.network(xb))

model = ResNet()



def to_device(data, device):
    """Move tensor(s) to chosen device"""
    if isinstance(data, (list,tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)

def get_default_device():
    """Pick GPU if available, else CPU"""
    if torch.cuda.is_available():
        return torch.device('cuda')
    else:
        return torch.device('cpu')

def predict_image(img, model):
    # Convert to a batch of 1
    xb = to_device(img.unsqueeze(0), device)
    # Get predictions from model
    yb = model(xb)
    # Pick index with highest probability
    prob, preds  = torch.max(yb, dim=1)
    # Retrieve the class label
    return dataset[preds[0].item()]
  



# ?????? ????????? ?????????
@app.route("/")
@app.route("/index")
def index():
    return flask.render_template('index.html')


# ????????? ?????? ??????
@app.route('/predict', methods=['POST'])
def make_prediction():
    if request.method == 'POST':

        # ????????? ?????? ?????? ??????
        file = request.files['image']
        if not file: return render_template('index.html', label="No Files")

        #????????? ?????? ?????? ??????
        image = Image.open(file)

        #????????? ??????
        example_image = transformations(image)

        #????????? ?????? ??????


        prediction = predict_image(example_image, loaded_model)
        return render_template('index.html', label=prediction)


if __name__ == '__main__':

    #device = get_default_device() 
    
    # ?????? ??????
    # ml/model.py ??? ?????? ??? ??????
    
    #?????? ?????? ??? ??????
    #model.pt ?????? ???????????????
    #loaded_model = torch.load('model.pt') 
    device = torch.device('cpu')
    
    loaded_model = torch.load('model.pt', map_location=device)
    #####????????? ?????? ?????? ???????????? ?????? #########
    #model = torch.load('./model/model.pt')
   
   
    # Flask ????????? ?????????
    app.run(host='0.0.0.0', port=8000, debug=True)
