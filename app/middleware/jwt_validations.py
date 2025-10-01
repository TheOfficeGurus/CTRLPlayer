from functools import wraps
from flask import request, jsonify
from dateutil import parser
import datetime
from authlib.jose import JsonWebEncryption as jwe
from app.config import Config as app_config
from app.exceptions.custom_exceptions import TokenExpired, TokenClaimsMismatch,TokenInvalidAuth
from app.utils.helpers import error_response
import json


def authorize(required_claims=None):
    def jwt_required(f):
        @wraps(f)
        def decorated_wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization',"")
            try:
                if app_config.__OU__ =="":
                    raise TokenExpired()
                
                if not auth_header:
                    raise TokenInvalidAuth()
                
                if "Bearer" not in auth_header:
                    raise TokenInvalidAuth()
                
                payload = jwe().deserialize_compact(auth_header.split('Bearer ')[1], app_config._KEY_)
                data = json.loads(payload['payload'].decode())
                if required_claims:
                    for k, v in required_claims.items():
                        if data.get(k) != v:
                            raise TokenClaimsMismatch()
                        
                if 'exp' in data:
                    exp = parser.parse(data['exp'])
                    if datetime.datetime.now(tz=datetime.timezone.utc) > exp:
                        raise TokenExpired()
                    
            except TokenInvalidAuth as e:
                return error_response(str(e.message)), 403
            except TokenExpired as e:
                return error_response(str(e.message),401)
            except TokenClaimsMismatch as e:
                return error_response(str(e.message),403)
            except Exception as e:
                return error_response(f' invalid token: {str(e)}',500)
                
            return f(*args, **kwargs)
        return decorated_wrapper
    return jwt_required
    