from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

import os
import joblib
import numpy as np
import pandas as pd
import re
from PIL import Image
from konlpy.tag import Okt
from tensorflow import keras
from tensorflow.keras.models import load_model
from keras.applications.vgg16 import VGG16, decode_predictions
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from clust_util import cluster_util


app = Flask(__name__)
app.debug = True

vgg = VGG16()
okt = Okt()
movie_lr = None
movie_lr_dtm = None
def load_movie_lr():
    global movie_lr, movie_lr_dtm
    movie_lr = joblib.load(os.path.join(app.root_path, 'model/movie_lr.pkl'))
    movie_lr_dtm = joblib.load(os.path.join(app.root_path, 'model/movie_lr_dtm.pkl'))

def tw_tokenizer(text):
    # 입력 인자로 들어온 text 를 형태소 단어로 토큰화 하여 list 객체 반환
    tokens_ko = okt.morphs(text)
    return tokens_ko

movie_nb = None
movie_nb_dtm = None
def load_movie_nb():
    global movie_nb, movie_nb_dtm
    movie_nb = joblib.load(os.path.join(app.root_path, 'model/movie_nb.pkl'))
    movie_nb_dtm = joblib.load(os.path.join(app.root_path, 'model/movie_nb_dtm.pkl'))




model_iris_lr = None
model_iris_svm = None
model_iris_dt = None
model_iris_deep = None
def load_iris():
    global model_iris_lr, model_iris_svm, model_iris_dt,  model_iris_deep
    model_iris_lr = joblib.load(os.path.join(app.root_path,'model/iris_lr.pkl'))
    model_iris_svm = joblib.load(os.path.join(app.root_path,'model/iris_svm.pkl'))
    model_iris_dt = joblib.load(os.path.join(app.root_path,'model/iris_dt.pkl'))
    model_iris_deep = load_model(os.path.join(app.root_path,'model/iris_deep.hdf5'))

model_indians = None

def load_indians():
    global  model_indians
    model_indians = load_model(os.path.join(app.root_path, 'model/best_model.hdf5'))


def nb_transform(review):
    stopwords=['의','가','이','은','들','는','좀','잘','걍','과','도','를','으로','자','에','와','한','하다']
    review = review.replace("[^ㄱ-ㅎㅏ-ㅣ가-힣 ]","")
    morphs = okt.morphs(review, stem=True)
    temp = ' '.join(morph for morph in morphs if not morph in stopwords)
    return temp




@app.route('/')
def index():
    menu = {'home':True, 'rgrs':False, 'stmt':False, 'clsf':False, 'clst':False, 'user':False}
    return render_template('home.html', menu=menu)

@app.route('/regression', methods=['GET', 'POST'])
def regression():
    menu = {'home':False, 'rgrs':True, 'stmt':False, 'clsf':False, 'clst':False, 'user':False}
    if request.method == 'GET':
        return render_template('regression.html', menu=menu)
    else:
        sp_names = ['Setosa', 'Versicolor', 'Virginica']
        slen = float(request.form['slen'])      # Sepal Length
        plen = float(request.form['plen'])      # Petal Length
        pwid = float(request.form['pwid'])      # Petal Width
        sp = int(request.form['species'])       # Species
        species = sp_names[sp]
        swid = 0.63711424 * slen - 0.53485016 * plen + 0.55807355 * pwid - 0.12647156 * sp + 0.78264901
        swid = round(swid, 4)
        iris = {'slen':slen, 'swid':swid, 'plen':plen, 'pwid':pwid, 'species':species}
        return render_template('reg_result.html', menu=menu, iris=iris)



@app.route('/sentiment', methods=['GET', 'POST'])
def sentiment():
    menu = {'home':False, 'rgrs':False, 'stmt':True, 'clsf':False, 'clst':False, 'user':False}
    if request.method == 'GET':
        return render_template('sentiment.html', menu=menu)
    else:
        res_str = ['부정', '긍정']
        review = request.form['review']
        #lr처리
        review_lr = re.sub(r"\d+", " ",review)
        review_lr_dtm = movie_lr_dtm.transform([review_lr])
        result_lr = res_str[movie_lr.predict(review_lr_dtm)[0]]
        #nb처리
        review_nb = nb_transform(review)
        review_nb_dtm = movie_nb_dtm.transform([review_nb])
        result_nb = res_str[movie_nb.predict(review_nb_dtm)[0]]
        # 결과처리
        movie = {'review':review, 'result_lr':result_lr,'result_nb':result_nb}
        return render_template('sent_result.html',  menu=menu, movie=movie) 





@app.route('/classification', methods=['GET', 'POST'])
def classification():
    menu = {'home':False, 'rgrs':False, 'stmt':False, 'clsf':True, 'clst':False, 'user':False}
    if request.method == 'GET':
        return render_template('classification.html', menu=menu)
    else:
        try:
            f = request.files['image']
            filename = os.path.join(app.root_path, 'static/images/uploads/') + \
                        secure_filename(f.filename)
            f.save(filename)
            img = np.array(Image.open(filename).resize((224, 224)))
            yhat = vgg.predict(img.reshape(-1, 224, 224, 3))
            label_key = np.argmax(yhat)
            label = decode_predictions(yhat)
            label = label[0][0]
        except:
            return render_template('classification.html', menu=menu)

        return render_template('cla_result.html', menu=menu,
                                filename = secure_filename(f.filename),
                                name = label[1], pct='%.2f' % (label[2]*100))
        




@app.route('/classification_iris', methods=['GET', 'POST'])
def classification_iris():
    menu = {'home':False, 'rgrs':False, 'stmt':False, 'clsf':True, 'clst':False, 'user':False}
    if request.method == 'GET':
        return render_template('classification_iris.html', menu=menu)
    else:
        sp_names = ['Setosa', 'Versicolor', 'Virginica']
        slen = float(request.form['slen'])      # Sepal Length
        swid = float(request.form['swid'])      # Sepal width
        plen = float(request.form['plen'])      # Petal Length
        pwid = float(request.form['pwid'])      # Petal Width
        test_data = np.array([slen, swid, plen, pwid]).reshape(1,4)
        species_lr = sp_names[model_iris_lr.predict(test_data)[0]]
        species_svm = sp_names[model_iris_svm.predict(test_data)[0]]
        species_dt = sp_names[model_iris_dt.predict(test_data)[0]]
        species_deep = sp_names[model_iris_deep.predict_classes(test_data)[0]]
        iris = {'slen':slen, 'swid':swid, 'plen':plen, 'pwid':pwid, 'species_lr':species_lr, 'species_svm':species_svm, 'species_dt':species_dt, 'species_deep':species_deep}
        return render_template('cla_iris_result.html', menu=menu, iris=iris)
       
@app.route('/classification_indians', methods=['GET', 'POST'])
def classification_indians():
    menu = {'home': False, 'intro':False, 'rgrs': False, 'stmt': False, 'clsf': True, 'clst': False, 'user': False}
    if request.method == 'GET':
        return render_template('classification_indians.html', menu=menu)
    else:
        sp_names = ['당뇨 아님', '당뇨']
        pregnant = int(request.form['pregnant'])
        plasma = int(request.form['plasma'])
        pressure = int(request.form['pressure'])
        thickness = int(request.form['thickness'])
        insulin = int(request.form['insulin'])
        BMI = float(request.form['bmi'])
        pedigree = float(request.form['pedigree'])
        age = int(request.form['age'])

        test_data = np.array([pregnant, plasma, pressure, thickness, insulin, BMI, pedigree, age]).reshape(1, 8)
        results = sp_names[model_indians.predict_classes(test_data)[0][0]]

        indians = {'pregnant': pregnant, 'plasma': plasma, 'pressure': pressure, 'thickness': thickness,
                'insulin': insulin, 'bmi': BMI,
                'pedigree': pedigree, 'age':age, 'result': results}
        return render_template('clf_indians_result.html', menu=menu, indians=indians)


@app.route('/clustering', methods=['GET', 'POST'])
def clustering():
    menu = {'home':False, 'rgrs':False, 'stmt':False, 'clsf':False, 'clst':True, 'user':False}
    if  request.method == 'GET':
        return render_template('clustering.html', menu=menu)
    else:
        f = request.files['csv']
        filename = os.path.join(app.root_path, 'static/images/uploads/') + \
                    secure_filename(f.filename)
        f.save(filename)
        ncls = int(request.form['K'])
        cluster_util(app, ncls, secure_filename(f.filename))
        img_file = os.path.join(app.root_path, 'static/images/kmc.png')
        mtime = int(os.stat(img_file).st_mtime)
        return render_template('clu_result.html', menu=menu, K=ncls, mtime=mtime)





@app.route('/sseungki', methods=['GET', 'POST'])
def seungki():
    menu = {'home':False, 'rgrs':False, 'stmt':False, 'clsf':False, 'clst':False, 'user':True}
    if request.method == 'GET':
        return render_template('sseungki.html',menu=menu)
    else:
        pass


@app.route('/member/<name>')
def member(name):
    menu = {'home':False, 'rgrs':False, 'stmt':False, 'clsf':False, 'clst':False, 'user':True}
    nickname = request.args.get('nickname', '별명: 없음')
    return render_template('user.html', menu=menu, name=name, nickname=nickname)




if __name__ == '__main__':
    load_movie_nb()
    load_movie_lr()      
    load_indians()        
    load_iris()
    app.run()
    # app.run(host='0.0.0.0')
