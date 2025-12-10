from flask import Blueprint, request
from app.services.users_service import UserService
from app.middleware.jwt_validations import authorize
from app.exceptions.custom_exceptions import InvalidRequestError, TokenClaimsMismatch
import app.utils.helpers as message

users_bp = Blueprint('users', __name__, url_prefix='/users')

# @users_bp.route('/verify', methods=['POST'])
# @authorize(required_claims={'service': 'ATS'})
# def verify():
#     try:
#         if request.json is None:
#             raise InvalidRequestError()
#         if [key for key in request.json if key not in ['username', 'fullname']]:
#             raise TokenClaimsMismatch()
            
#         result = UserService.validate_username(request.json)
        
#     except InvalidRequestError as e:
#         return message.error_response(str(e.message))
#     except TokenClaimsMismatch as e:
#         return message.error_response(str(e.message))
#     except Exception as e:
#         return message.error_response(f'login: {str(e)}',500)
    
#     return message.success_response(result)

@users_bp.route('/verify_fullname', methods=['POST'])
@authorize(required_claims={'service': 'ATS'})
def verify_fullname():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['fullname']]:
            raise TokenClaimsMismatch()
            
        result = UserService.validate_fullname(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'login: {str(e)}',500)
    
    return message.success_response(result)

@users_bp.route('/assignEmployeeId',methods=['POST'])
@authorize(required_claims={'service': 'ATS'})
def modify():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['username', 'fullname','employeeId','updatedBy']]:
            raise TokenClaimsMismatch()
    
        result = UserService.modify_user(request.json)
        if [key for key in result if key in ['Error']]:
            return message.error_response(result)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'login: {str(e)}',500)
    
    return message.success_response(result)

@users_bp.route('/getByEmpid', methods=['POST'])
@authorize(required_claims={'service': 'LEXDATA', 'service':'FLUX'})
def getByEmpid():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['EmployeeID']]:
            raise TokenClaimsMismatch()
            
        result = UserService.validate_empid(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'getByEmpid: {str(e)}',500)
    
    return message.success_response(result)

@users_bp.route('/assingSuppervisor', methods=['POST'])
@authorize(required_claims={'service': 'FLUX'})
def assingSuppervisor():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['guru_employeeID','sup_employeeID','updatedBy']]:
            raise TokenClaimsMismatch
        
        result = UserService.assing_New_Supervisor(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'assignationSup: {str(e)}',500)
    return message.success_response(result)