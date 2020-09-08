from flask import Flask, render_template, session, redirect, url_for, session, Response
from flask_wtf import FlaskForm
from wtforms import TextField,SubmitField
from wtforms.validators import NumberRange

from api.rossmann import Rossmann

import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import joblib
import json

def return_prediction(sample_json):
    
    # For larger data features, you should probably write a for loop
    # That builds out this array for you
    
    test_json = json.loads(sample_json)

    if test_json:  # there is data

        if isinstance(test_json, dict):  # unique example
            test_raw = pd.DataFrame(test_json, index=[0])

        else:  # multiple example
            test_raw = pd.DataFrame(test_json, columns=test_json[0].keys())

        # Instantiate Rossmann class
        pipeline = Rossmann()

        # data cleaning
        df1 = pipeline.data_cleaning(test_raw)

        # feature engineering
        df2 = pipeline.feature_engineering(df1)

        # data preparation
        df3 = pipeline.data_preparation(df2)

        # prediction

        df_response = pipeline.get_prediction(test_raw, df3)

        return df_response

    else:
        return Response('{}', status=200, mimetype='application/json')


app = Flask(__name__)
# Configure a secret SECRET_KEY
# We will later learn much better ways to do this!!
app.config['SECRET_KEY'] = 'mysecretkey'


# Now create a WTForm Class
# Lots of fields available:
# http://wtforms.readthedocs.io/en/stable/fields.html
class Vendas(FlaskForm):
    loja = TextField('Loja(s):')

    submit = SubmitField('Prever vendas')



@app.route('/', methods=['GET', 'POST'])
def index():

    # Create instance of the form.
    form = Vendas()
    # If the form is valid on submission (we'll talk about validation next)
    if form.validate_on_submit():
        # Grab the data from the breed on the form.

        session['loja'] = form.loja.data

        return redirect(url_for("prediction"))


    return render_template('home.html', form=form)


@app.route('/prediction', methods=['GET', 'POST'])
def prediction():

    aux = session['loja']
    aux = map(int, aux.split(','))

    # loading test dataset
    df_sales_raw = pd.read_csv('./data/test.csv')
    df_store_raw = pd.read_csv('./data/store.csv', low_memory=False)
    # merge for test data
    df_test = pd.merge(df_sales_raw, df_store_raw, how='left', on='Store')

    # filter selected data from user
    df_test = df_test[df_test['Store'].isin(aux)]

    # convert Dataframe to json
    data = json.dumps(df_test.to_dict(orient='records'))

    #predict results
    res = return_prediction(data)

    #convert to dataframe
    res = pd.DataFrame(res)

    #merge with original store column
    df_test.reset_index(inplace=True)
    res = pd.concat([df_test[['Store', 'Open']], res], axis=1).rename(columns={0: "Sales"})

    # remove closed days
    res = res[res['Open'] != 0]
    res = res.drop('Open', axis=1)

    #group sales by store
    df = res[['Store', 'Sales']].groupby('Store').sum().reset_index()
    df.set_index('Store',inplace=True)
    df['Sales']=df['Sales'].apply(lambda x: round(x, 2))
    df.rename(columns={"Sales": "Sales (R$)"},inplace=True)

    return render_template('prediction.html', tables=[df.to_html(classes='data')], titles=df.columns.values)