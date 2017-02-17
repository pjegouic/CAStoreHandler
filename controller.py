from flask import Flask, redirect, request, jsonify, session
import sqlite3
import json
import xmltodict
from OAuthentication import OAuthentication
from user import User


app = Flask(__name__)
app.secret_key = 'BAZOOM'
user = User()
oauth = OAuthentication()

@app.route('/auth', methods=['GET'])
def authentication():
    oauth.getRequestToken()
    user.oauth_session = oauth
    return redirect(oauth.oauth_session.authorization_url(oauth.authorization_url))


@app.route('/home', methods=['GET'])
def home():
    if user.oauth_session is None :
        return redirect('/auth')
    else:
        initUser()
        return str(user.technical_id)

@app.route('/comptesBAM', methods=['GET'])
def getBAMs():
    if user.oauth_session is None :
        return redirect('/auth')
    else:
        url = 'https://www.creditagricolestore.fr/castore-data-provider/rest/V1/utilisateurs/' + str(user.technical_id) +'/comptesBAM'
        response = oauth.oauth_session.get(url).json()
        print('BAMACCOUNTS : ')
        print(response)
        user.compteBAM_id = response['compteBAMDTOs'][0]['id']
        return jsonify(response)

@app.route('/comptes')
def getComptes():
    if user.oauth_session is None :
        return redirect('/auth')
    else:
        url = 'https://www.creditagricolestore.fr/castore-data-provider/rest/V1/utilisateurs/' + str(
            user.technical_id) + '/comptesBAM/' + str(user.compteBAM_id) + '/comptes'
        response = oauth.oauth_session.get(url).json()
        print('ACCOUNTS : ')
        print(response)
        user.compte_id = response['compteDTOs'][0]['id']
        return jsonify(response)

@app.route('/operations')
def getOperations():
    if user.oauth_session is None :
        return redirect('/auth')
    else:
        getBAMs()
        getComptes()
        url = 'https://www.creditagricolestore.fr/castore-data-provider/rest/V1/utilisateurs/' + str(
            user.technical_id) + '/comptesBAM/' + str(user.compteBAM_id) + '/comptes/' + str(user.compte_id) + '/operations'
        response = oauth.oauth_session.get(url).json()
        user.transaction_list = response['operationDTOs']
        persistOperations(response['operationDTOs'])
        return jsonify(response)

@app.route('/callback')
def initUser():
    print("VERIFIER :")
    print(request.args.get('oauth_verifier'))
    oauth.verifier = request.args.get('oauth_verifier')
    oauth.oauth_token = request.args.get('oauth_token')
    oauth.getAccessToken()
    session['credentials'] = oauth.credentials
    technical_id = oauth.oauth_session.get('https://www.creditagricolestore.fr/castore-data-provider/rest/V1/session').json()
    print(technical_id)
    user.technical_id = technical_id['id']
    return redirect('/operations')

def persistOperations(operationList):
    conn = sqlite3.connect('OperationDB.db')
    columns = ['dateValeur',  'montant',  'libelleOperationMediaMicro1', 'libelleOperationMediaMicro2','libelleCourt', 'date']
    conn.execute('''CREATE TABLE if not exists OPERATIONS (date, dateValeur, libelleCourt,libelleOperationMediaMicro1, libelleOperationMediaMicro2, montant, marchand, marchand_sav_tel, purchase_category) ''')
    print('OPERATION LIST')
    print(type(operationList))
    print(operationList)
    conn.executemany("INSERT INTO OPERATIONS (dateValeur,montant,libelleOperationMediaMicro1,libelleOperationMediaMicro2,libelleCourt,date) VALUES (:dateValeur,:montant,:libelleOperationMediaMicro1,:libelleOperationMediaMicro2,:libelleCourt,:date)", operationList)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run()


