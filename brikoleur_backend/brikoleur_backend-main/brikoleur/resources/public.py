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
from flask_mail import Mail , Message


pub = Blueprint('pub',__name__)

@pub.route('/login')
def login():
	auth = request.authorization

	if not auth or not auth.username or not auth.password:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

	user = Users.query.filter_by(email=auth.username).first()

	if not user:
		return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

	if check_password_hash(user.password, auth.password):
		token = jwt.encode({
			'public_id' : user.public_id, 
			'expiration' :str( datetime.datetime.utcnow() + datetime.timedelta(minutes=30))}, 
			pub.config['SECRET_KEY'])

		return jsonify({'token' : token.decode('utf_8')})

	return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})


@pub.route('/register', methods=['POST'])
def register():
	data = request.get_json()
	test=Users.query.filter_by(email=data['email']).first()
	if test:
		return jsonify({'message' : 'email alredy used ,try to login!'})
	if data['brikoleur']:
		hashed_password = generate_password_hash(data['password'], method='sha256')
		new_user = Users(public_id=str(uuid.uuid4()), name=data['name'],email=data['email'], password=hashed_password, admin=False,brikoleur=True,tel=data['tel'],location=data['location'])
		db.session.add(new_user)
		db.session.commit()
		user_data = BricoleurData(domaine=data['domaine'],seniority=data['seniority'],wallet=0,profile=data['profile'],user_id=new_user.id)
		db.session.add(user_data)
		db.session.commit()
		return jsonify({'message' : 'New user created!'})
	hashed_password = generate_password_hash(data['password'], method='sha256')
	new_user = Users(public_id=str(uuid.uuid4()), name=data['name'],email=data['email'], password=hashed_password, admin=False,brikoleur=False,tel=data['tel'],location=data['location'])
	db.session.add(new_user)
	db.session.commit()

	return jsonify({'message' : 'New user created!'})


def send_reset_email(user):
	token = jwt.encode({
			'public_id' : user.public_id, 
			'expiration' :str( datetime.datetime.utcnow() + datetime.timedelta(minutes=30))}, 
			pub.config['SECRET_KEY'])
	msg = Message('Password Reset Request',
				  sender='noreply@demo.com',
				  recipients=[user.email])
	msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token.decode('utf_8'), _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
	mail.send(msg)


@pub.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	data = request.get_json()
	user = Users.query.filter_by(email=data['email']).first()
	if user :
		send_reset_email(user)
		return jsonify({'message' : 'email sent!'})
	else :
		return jsonify({'message' : 'no info!'})
	


@pub.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	try: 
		data = jwt.decode(token, pub.config['SECRET_KEY'])
		current_user = Users.query.filter_by(public_id=data['public_id']).first()
	except:
		return jsonify({'message' : 'Token is invalid!'}), 401
	data = request.get_json()
	hashed_password = generate_password_hash(data['password'], method='sha256')
	current_user.password=hashed_password
	db.session.commit()
	return jsonify({'message' : 'password updated!'})



@pub.route('/update_profile', methods=['POST'])
@token_required
def update_profile(current_user):
	data = request.get_json()
	if 'email' in data :
		user = Users.query.filter_by(email=data["email"]).first()
		if user :
			return jsonify({'message' : 'email alredy used !'})
		else :
			current_user.email = data['email']
	elif 'name' in data :
		current_user.name = data['name']
	elif 'password' in data :
		hashed_password = generate_password_hash(data['password'], method='sha256')
		current_user.password = hashed_password
	elif 'tel' in data :
		current_user.tel = data['tel']
	elif 'location' in data :
		current_user.location = data['location']
	if current_user.brikoleur :
		usr_data = BricoleurData.query.filter_by(user_id=current_user.id).first()
		if 'domaine' in data :
			usr_data.domaine = data['domaine']
		elif 'seniority' in data :
			usr_data.seniority = data['seniority']
		elif 'wallet' in data :
			usr_data.wallet = data['wallet']
		elif 'profile' in wallet :
			usr_data.profile = data['profile']
	db.session.commit()
	return jsonify({'message' : 'info updated !'})

@pub.route('/delete_profil', methods=['DELETE'])
@token_required
def delete_profil(current_user):
	if current_user.brikoleur :
		data = BricoleurData.query.filter_by(user_id=current_user.id).first()
		db.session.delete(data)
		db.session.commit()
	db.session.delete(current_user)
	db.session.commit()
	return jsonify({'message' : 'done !'})