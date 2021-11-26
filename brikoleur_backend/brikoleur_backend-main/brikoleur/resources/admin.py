from flask import Blueprint , request
from brikoleur.models.models import *
import datetime 
import bcrypt
import pydicom.uid
from pydicom.uid import generate_uid
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import uuid

adm = Blueprint('adm',__name__)


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

@adm.route('/admin', methods=['GET'])
@token_required
def get_all_users(current_user):

	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function!'})

	users = Users.query.all()

	output = []

	for user in users:
		user_data=tojson(user.public_id)
		output.append(user_data)

	return jsonify({'users' : output})

@adm.route('/admin/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function!'})

	user = Users.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message' : 'No user found!'})

	user_data = tojson(user.public_id)

	return jsonify({'user' : user_data})



@adm.route('/admin/<public_id>', methods=['PUT'])
@token_required
def promote_user(current_user, public_id):
	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function!'})

	user = Users.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message' : 'No user found!'})

	user.admin = True
	user.brikoleur=False
	db.session.commit()

	return jsonify({'message' : 'The user has been promoted!'})



@adm.route('/admin/<public_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, public_id):
	if not current_user.admin:
		return jsonify({'message' : 'Cannot perform that function!'})

	user = Users.query.filter_by(public_id=public_id).first()

	if not user:
		return jsonify({'message' : 'No user found!'})

	db.session.delete(user)
	db.session.commit()
	if user.brikoleur:
		data = BricoleurData.query.filter_by(user_id=user.id).first()
		db.session.delete(data)
		db.session.commit()

	return jsonify({'message' : 'The user has been deleted!'})
