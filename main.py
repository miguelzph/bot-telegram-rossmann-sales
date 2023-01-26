import telebot
import os
import rossmann_api
import pandas as pd

from replit import db

# TELEGRAM BOT
KEY_BOT = os.environ['key_bot']

bot = telebot.TeleBot(KEY_BOT)


# DATABASE
def record_user(id):
    if f'{id}' not in db.keys():
        db[f'{id}'] = {
            'command_store': False,
            'store_number': None,
            'aux': None
        }


def acess_records(id, field, operation='retrive', information=None):
    if operation == 'retrive':
        return db[f'{id}'][field]
    elif operation == 'save':
        db[f'{id}'][field] = information
        return None


# ONLY ONE STORE
@bot.message_handler(commands=["store"])
def store_sales(mensagem):
    text = 'Qual o número da loja?'
    bot.send_message(mensagem.chat.id, text)

    acess_records(mensagem.chat.id,
                  field='command_store',
                  operation='save',
                  information=True)


def store_command_true(mensagem):
    if acess_records(mensagem.chat.id, 'command_store') == True:
        return True
    else:
        return False


@bot.message_handler(func=store_command_true)
def send_predict_value(mensagem):
    # maybe for future use
    store_number = mensagem.text
    acess_records(mensagem.chat.id,
                  'store_number',
                  operation='save',
                  information=store_number)

    # real task
    text = 'Consultando a API...'
    bot.send_message(mensagem.chat.id, text)
    sales_value = rossmann_api.return_predict_from_api(store_id=store_number)
    bot.send_message(mensagem.chat.id, sales_value)
    acess_records(mensagem.chat.id,
                  'command_store',
                  operation='save',
                  information=False)


# ALL STORES
@bot.message_handler(commands=["all_stores"])
def all_store_sales(mensagem):
    text = 'Consultando a API e gerando csv...'
    bot.send_message(mensagem.chat.id, text)

    sales_df = rossmann_api.return_predict_from_api(all_stores=True)

    # a ser deletado ou usado em novas requisicoes do mesmo dia
    file_path = f'data/temp/store_predict_sales_{mensagem.chat.id}.csv'
    sales_df.to_csv(file_path, sep=";", index=False)

    with open(file_path, 'r') as doc:
        bot.send_document(mensagem.chat.id, doc)


# START
@bot.message_handler(commands=["start"])
def initial_contact(mensagem):
    texto = """
Bem vindo! Bot para obter a previsão de vendas da rede de farmácias Rossmann (6 semanas).

Obs: A primeira informação sobre a loja vai demorar alguns minutos (o serviço está hospedado gratuitamente), e nesse caso pode ser necessário enviar uma nova mensagem."""

    bot.send_message(mensagem.chat.id, texto)

    responder(mensagem)


# STANDART
def verify(mensagem):
    return True


@bot.message_handler(func=verify)
def responder(mensagem):
    record_user(mensagem.chat.id)
    texto = """
    O que você deseja?
    /store Previsão de uma loja específica
    /all_stores Previsão de todas as lojas"""
    bot.reply_to(mensagem, texto)


bot.polling()
