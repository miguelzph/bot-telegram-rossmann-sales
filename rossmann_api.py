import json
import pandas as pd
import requests


def load_data(store_id, all_stores):
    # loading test dataset
    df_test = pd.read_csv('data/test.csv')
    df_store_raw = pd.read_csv('data/store.csv')

    # merge
    df_test = df_test.merge(df_store_raw, on='Store')

    # choose store for predction
    if all_stores == False:
        df_test = df_test[df_test['Store'] == store_id]
    else:
        pass  # continuos with all stores

    return df_test


def filter_data(df):
    # remove closed days
    df = df[df['Open'] != 0]
    df = df[~df['Open'].isnull()]
    df = df.drop(columns=['Id'])

    # convert DataFrame to json
    data_j = df.to_json(orient='records')

    return data_j


def call_api(data_j):

    # API call
    # url = 'https://rossman-prediction-sales.herokuapp.com/rossmann/predict'
    url = 'https://rossmann-sales.onrender.com/rossmann/predict'
    header = {'Content-type': 'application/json'}
    data = data_j

    r = requests.post(url, data=data, headers=header)
    print(f'Status Code {r.status_code}')

    d1 = pd.DataFrame(r.json())
    d2 = d1[['Store', 'prediction']].groupby('Store').sum().reset_index()

    return d2


def return_predict_from_api(store_id=None, all_stores=False):
    # pendente melhorar logica --> store_id=None já pode significar todas as lojas
    try:
        # test and transform if it's a int
        if store_id != None:
            try:
                store_id = int(store_id)
            except:
                return f'"{store_id}" não corresponde ao código de uma loja, lembre-se que deve ser um número inteiro'

        # load data
        df_store = load_data(store_id, all_stores)

        # if data is not empty
        if len(df_store) != 0:
            df_store_filtered = filter_data(df_store)
            response_df = call_api(df_store_filtered)

            if all_stores == False:  # only one store
                predict_value = response_df["prediction"].values[0]
                predict_value = f'{predict_value:_.2f}'.replace('.',
                                                                ',').replace(
                                                                    '_', '.')

                return f'R$ {predict_value} é o valor previsto para as vendas da loja {store_id} nas próximas 6 semanas'
            else:  # all stores
                response_df['prediction'] = response_df['prediction'].apply(
                    lambda x: round(x, 2))

                return response_df
        else:
            return f'Não foi possível encontrar a loja de código {store_id}'
    except:
        return 'Erro de requisição, por favor tente novamente mais tarde.'
