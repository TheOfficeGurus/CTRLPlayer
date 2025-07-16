from functools import wraps
from flask import request, jsonify
from dateutil import parser
import datetime
from authlib.jose import JsonWebEncryption as jwe
from app.config import Config as app_config
from app.exceptions.custom_exceptions import TokenInvalidCredential , TokenExpired, TokenClaimsMismatch
import json


def authorize(required_claims=None):
    def jwt_required(f):
        @wraps(f)
        def decorated_wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization',"")
            if not auth_header:
                return jsonify({'error': 'Token missing'}), 401
            token = auth_header.split(" ")[1]
            try:
                payload = jwe().deserialize_compact(token, app_config._KEY_)
                data = json.loads(payload['payload'].decode())
                if required_claims:
                    for k, v in required_claims.items():
                        if data.get(k) != v:
                            raise TokenClaimsMismatch()
                if 'exp' in data:
                    exp = parser.parse(data['exp'])
                    if datetime.datetime.now(tz=datetime.timezone.utc) > exp:
                        raise TokenExpired()
            except TokenInvalidCredential as e:
                return jsonify({'error': f'{e.message}'}), 401
            except TokenExpired as e:
                return jsonify({'error': f'{e.message}'}), 401
            except TokenClaimsMismatch as e:
                return jsonify({'error': f'{e.message}'}),403
            except Exception as e:
                return jsonify({'error': f' invalid token: {str(e)}'}),500
                
            return f(*args, **kwargs)
        return decorated_wrapper
    return jwt_required
    
    
# # if __name__ == "__main__":
#     # Example usage
#     payload = {
#     "service": "ATS",
#     "environment": "development",
#     "phrase": "vamarela"
# }
#     token = create_jwt_token(payload)
#     print(f"Generated JWT Token: {token}")
    
#     decoded_payload = decode_jwt_token(token)
    
#     print(f"Decoded Payload: {decoded_payload}")