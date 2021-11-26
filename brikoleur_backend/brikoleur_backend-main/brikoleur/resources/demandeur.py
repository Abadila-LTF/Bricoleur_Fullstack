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

dem = Blueprint('dem',__name__)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401

        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = Users.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@dem.route('/demandeur', methods=['GET'])
@token_required
def get_all_brikoleurs(current_user):

    if current_user.admin or current_user.brikoleur :
        return jsonify({'message' : 'Cannot perform that function!'})

    users = Users.query.filter_by(brikoleur=True).all()

    output = []

    for user in users:
        user_data=tojson(user.public_id)
        output.append(user_data)

    return jsonify({'brikoleurs' : output})

@dem.route('/demandeur/<public_id>', methods=['GET'])
@token_required
def get_one_brikoleur(current_user, public_id):

    if current_user.admin or current_user.brikoleur :
        return jsonify({'message' : 'Cannot perform that function!'})

    user = Users.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    user_data = tojson(user.public_id)

    return jsonify({'user' : user_data})

@dem.route('/demandeur/request/<public_id>', methods=['POST'])
@token_required
def send_request(current_user, public_id):

    if current_user.admin or current_user.brikoleur :
        return jsonify({'message' : 'Cannot perform that function!'})

    user = Users.query.filter_by(public_id=public_id ,admin=False , brikoleur = True).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    request = Mission(demandeur_id=current_user.id , brikoleur_id = user.id ,accepted=False)
    db.session.add(request)
    db.session.commit()
    return jsonify({'message' : 'request sent !'})

@dem.route('/demandeur/request/<public_id>', methods=['DELETE'])
@token_required
def undo_request(current_user, public_id):

    if current_user.admin or current_user.brikoleur :
        return jsonify({'message' : 'Cannot perform that function!'})

    user = Users.query.filter_by(public_id=public_id ,admin=False , brikoleur = True).first()

    if not user:
        return jsonify({'message' : 'No user found!'})

    mision = Mission.query.filter_by(demandeur_id=current_user.id,brikoleur_id=user.id).first()
    
    if not mision :
        return jsonify({'message' : 'there is no request to this brikoleur !'})

    if mision.accepted :
        return jsonify({'message' : 'Request Alredy accepted!'})
    db.session.delete(mision)
    db.session.commit()


    return jsonify({'message' : 'request deleted !'})


@dem.route('/demandeur/request', methods=['GET'])
@token_required
def check_requests(current_user):

    if current_user.admin or current_user.brikoleur :
        return jsonify({'message' : 'Cannot perform that function!'})


    requests = Mission.query.filter_by(demandeur_id=current_user.id).all()
    accepted_requests=[]
    pending_requests=[]
    for request in requests:
        data={}
        data['to brikoleur'] = request.brikoleur_id
        data['sent in'] = request.date
        if request.accepted:
            accepted_requests.append(data)
        else:
            pending_requests.append(data)

    return jsonify({'accepted' : accepted_requests ,
                    'pending' : pending_requests})