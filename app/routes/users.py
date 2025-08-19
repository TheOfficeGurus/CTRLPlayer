import json
from flask import Blueprint, request, jsonify
from app.services.auth_service import AuthService
from app.services.users_service import UserService
from app.middleware.jwt_validations import authorize
from app.exceptions.custom_exceptions import InvalidRequestError, TokenClaimsMismatch
import app.utils.helpers as message

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/verify', methods=['POST']) #type: ignore
@authorize()
def verify():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['username', 'fullname']]:
            raise TokenClaimsMismatch()
        
    ### validate user cretentials here
    ##TODO: implement user validation logic with database 
    
        result = UserService.validate_users(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'login: {str(e)}',500)
    
    return message.success_response(result)

@users_bp.route('/verify_old', methods=['POST']) #type: ignore
@authorize()
def verify_old():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['username', 'fullname','employeeId']]:
            raise TokenClaimsMismatch()
        
    ### validate user cretentials here
    ##TODO: implement user validation logic with database 
    
        result = UserService.validate_users_odl(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'login: {str(e)}',500)
    
    return message.success_response(result)


@users_bp.route('/modify',methods=['POST'])
@authorize(required_claims={'service': 'ATS'})
def modify():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['username', 'fullname','employeeId']]:
            raise TokenClaimsMismatch()
    ### validate user cretentials here
    ##TODO: implement user validation logic with database 
    
        result = UserService.modify_user(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'login: {str(e)}',500)
    
    return message.success_response(result)