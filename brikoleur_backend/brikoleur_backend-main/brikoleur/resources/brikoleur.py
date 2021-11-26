from flask import Blueprint ,request
from brikoleur.models.models import *
import datetime 
import bcrypt
import pydicom.uid
from pydicom.uid import generate_uid
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid

bri = Blueprint('bri',__name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, bri.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@bri.route('/brikoleur', methods=['GET'])
@token_required
def check_requests_b(current_user):

    if not  current_user.brikoleur :
        return jsonify({'message' : 'Cannot perform that function!'})


    requests = Mission.query.filter_by(brikoleur_id=current_user.id).all()
    accepted_requests=[]
    pending_requests=[]
    for request in requests:
        data={}
        data['from demandeur'] = request.demandeur_id
        data['sent in'] = request.date
        if request.accepted:
            accepted_requests.append(data)
        else:
            pending_requests.append(data)

    return jsonify({'accepted' : accepted_requests ,
                    'pending' : pending_requests})

@bri.route('/brikoleur/<request_id>', methods=['POST'])
@token_required
def accept_request(current_user,request_id):

    if not  current_user.brikoleur :
        return jsonify({'message' : 'Cannot perform that function!'})


    requests = Mission.query.filter_by(brikoleur_id=current_user.id , id = request_id).first()

    if not requests :
        return jsonify({'message' : 'There is no request with thie Id!'})

    if requests.accepted :
        return jsonify({'message' : 'request alredy accepted!'})

    requests.accepted=True
    db.session.commit()

    return jsonify({'message' : 'request accepted !' })

@bri.route('/brikoleur/<request_id>', methods=['DELETE'])
@token_required
def refuse_request(current_user,request_id):

    if not  current_user.brikoleur :
        return jsonify({'message' : 'Cannot perform that function!'})


    requests = Mission.query.filter_by(brikoleur_id=current_user.id , id = request_id).first()

    if not requests :
        return jsonify({'message' : 'There is no request with thie Id!'})

    if requests.accepted :
        return jsonify({'message' : 'request alredy accepted!'})

    db.session.delete(requests)
    db.session.commit()

    return jsonify({'message' : 'request refused !' })

if __name__ == '__main__':
    bri.run(debug=True)