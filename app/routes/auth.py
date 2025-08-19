import json
from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.middleware.jwt_validations import authorize
from app.config import Config as app_config
from app.exceptions.custom_exceptions import InvalidRequestError, TokenClaimsMismatch
import app.utils.helpers as message
import os

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
# @authorize()
def login():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['service', 'environment', 'phrase']]:
            raise TokenClaimsMismatch()
        sk_list= []
        conf=[]
        services=[]
        
        with open(f'{app_config.__secret_path__}_{request.json['environment']}/2A3BD56F-2227-42BD-9378-32EA031982F8.json', 'r') as fh:
            for line in fh:
                sk_list.append(line.strip())
                
        if not sk_list[0]==request.json['phrase'] or not sk_list[1]==request.json['environment']:
            raise TokenClaimsMismatch()
        
        with open(f'{app_config.__secret_path__}_{request.json['environment']}/services.json', 'r') as fh:
            for line in fh:
                services.append(line)
                
        if not  request.json['service'] in services:
            raise TokenClaimsMismatch()
            
        with open(f'{app_config.__secret_path__}_{request.json['environment']}/conf.json', 'r') as fh:
            for line in fh:
                conf.append(line)
            
        if not conf:
            raise TokenClaimsMismatch()
        
        app_config.__OU__ = conf[0]
        
        
    ### validate user cretentials here
    ##TODO: implement user validation logic with database 
    
        token = AuthService.generate_token(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'login: {str(e)}',500)
    return jsonify({"token": f'Bearer {token}'}),200

@auth_bp.route('/verify',methods=['POST'])  # type: ignore
@authorize(required_claims={'service': 'ATS'})
def verify():
    return message.success_response("Token is valid")

@auth_bp.route('/radiocheck',methods=['GET']) # type:ignore
# @authorize(required_claims={'service': 'ATS'})
def radio_check():
    return message.success_response("Radio check is valid")