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
        
        AuthService.LoadConfigs(request.json)     
    
        token = AuthService.generate_token(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'login: {str(e)}',500)
    return jsonify({"token": f'Bearer {token}'}),200

@auth_bp.route('/radiocheck',methods=['GET']) # type:ignore
# @authorize(required_claims={'service': 'ATS'})
def radio_check():
    return message.success_response("Radio check is valid")