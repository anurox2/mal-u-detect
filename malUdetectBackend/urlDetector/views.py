from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import numpy

from keras.models import load_model
import pandas as pd
from tensorflow.python.keras.preprocessing import sequence
import pickle

def url_detection(url):
    url_test = [url]
    valid_chars = ''
    max_features = ''
    maxlen = ''

    try:
        with open("models/kos.txt", "rb") as f:
            set_of_values = pickle.load(f)
        valid_chars = set_of_values[0]
        max_features = set_of_values[1]
        maxlen = set_of_values[2]

    except Exception as e1:
        print('Error reading the values file')
        print(type(e1))
        print(e1.args)
    
    
    if(valid_chars == '' or max_features == '' or maxlen == ''):
        return -1
    else:
        pred_data = pd.DataFrame(url_test, columns = ['URLs'])
        X_pred = pred_data['URLs'].tolist()
        X_pred = [[valid_chars[y] for y in x] for x in X_pred]
        X_pred = sequence.pad_sequences(X_pred, maxlen=maxlen)

    model_loaded_from_file = ''
    try:
        model_loaded_from_file = load_model("models/Run_2021-05-09_23-45_ml_model1.h5") 
    except Exception as e:
        print("Model loading failed")
        print(type(e))
        print(e.args)
        return -1

    y_pred = model_loaded_from_file(X_pred)
    
    return y_pred[0][0]


@csrf_exempt
def index(request):
    mal_bool = False
    result = ''
    
    req_body = json.loads(request.body.decode('utf-8'))
    print("Printing request body", req_body['url'], request.body);
    url = req_body['url'].lower()

    result = url_detection(url)
    result = result.numpy()

    if(result == -1):
        result = "Error occured"
        mal_bool = False

    elif(result >= 0.1):
        mal_bool = True
    
    else:
        pass
    
    response_dict = {
        'URL': req_body['url'],
        'result': str(result),
        'Malicious': str(mal_bool)
    }
    return JsonResponse(dict(response_dict))
