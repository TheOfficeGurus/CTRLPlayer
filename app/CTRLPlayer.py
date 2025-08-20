import datetime
import json
import hashlib
from authlib.jose import JsonWebEncryption
from functools import wraps
from dateutil import parser
from flask import Flask,send_from_directory,abort,Response,request 
from flask_jwt_extended import JWTManager, jwt_required
from itsdangerous import URLSafeSerializer
from app.jwtValidations import create_jwt_token, decode_jwt_token

app = Flask(__name__)
base_uri = 'http://localhost:5000/'
SECRET_KEY = '4_v3c35_h4y_qu3_t0m4r_d3c1510n35_d1f1c1l35_p4r4_m4nt3n3r_3l_3qu1l1br10_3n_l4_g4l4x14...y_3n_3l_d1r3ct0r10_d3_u5u4r105.'
serializer = URLSafeSerializer(SECRET_KEY)

def authorize(required_claims=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization',"")
            if not auth_header:
                return Response(json.dumps({"error": "Authorization header missing"}), status=401, mimetype='application/json')
            token = auth_header.split(" ")[1] 
            
            passphrase = "4_v3c35_h4y_qu3_t0m4r_d3c1510n35..."
            key = hashlib.sha256(passphrase.encode()).digest()
            jwe = JsonWebEncryption()
            try:
                payload = jwe.deserialize_compact(token,key)
                data =json.loads(payload['payload'].decode())
            except Exception as e:
                return Response(json.dumps({"error": "invalid token"}), status=401, mimetype='application/json')
            
            # Validar claims requeridos
            if required_claims:
                for k, v in required_claims.items():
                    if data.get(k) != v:
                        return Response(json.dumps({"error": "Unauthorized: claim mismatch"}), status=403, mimetype='application/json')
            
            # Validar expiración del token
            if 'exp' in data:
                exp = parser.parse(data['exp'])
                if datetime.datetime.now(tz=datetime.timezone.utc) > exp:
                    return Response(json.dumps({"error": "Token expired"}), status=401, mimetype='application/json')
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/login',methods=['POST'])
def login():
    """
    Simulate a login endpoint that generates a JWT token.
    """
    if request.json is None:
        return Response(json.dumps({"error": "invalid request"}), status=400,mimetype='application/json')
    
    if [key for key in request.json if key not in ['service', 'environment', 'phrase']]:
        return Response(json.dumps({"error": "parameter missing or not provided"}),status=400,mimetype='application/json')   
        
    try: 
        token = create_jwt_token(request.json)
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), status=500, mimetype='application/json')
    
    return Response(json.dumps({"token": token}), mimetype='application/json')

@app.route('/verify',methods=['POST'])
@authorize(required_claims={'service': 'ATS','environment':'development'})
def verify():
    return Response(json.dumps({"message":"valid"}),mimetype='application/json')

@app.route('/validate_user',methods=['POST'])
@authorize(required_claims={'service': 'ATS'})
def validate_user():
    
    return Response(json.dumps({"message":"valid"}),mimetype='application/json')



if __name__ == "__main__":
    app.run(debug=True)
    app.run(host='0.0.0.0', port=5000, debug=False)