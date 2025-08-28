import datetime
from authlib.jose import JsonWebEncryption
import hashlib
import json

# Derivar clave de 256 bits
passphrase = "4_v3c35_h4y_qu3_t0m4r_d3c1510n35..."
key = hashlib.sha256(passphrase.encode()).digest()

# Inicializar JWE
jwe = JsonWebEncryption()

# Crear el encabezado JWE
protected_header = {
    "alg": "dir",
    "enc": "A256GCM"
}


def create_jwt_token(payload):
    """
    Function to create a JWT token.
    """
    token_json = json.loads(json.dumps(payload))
    token_json['exp'] = (datetime.datetime.now(tz=datetime.timezone.utc)+ datetime.timedelta(minutes=10)).isoformat()
    token_json['iat'] = (datetime.datetime.now(tz=datetime.timezone.utc)).isoformat()
    token_json['iss'] = f'CTRLPlayer for the galaxy'
    
    jwt_json = json.dumps(token_json).encode()
    jwt_token:str = jwe.serialize_compact(protected_header, jwt_json, key).__str__().replace('b\'', '').replace("'", '')
    return jwt_token

# Descifrar
def decode_jwt_token(token):
    """
    Function to decode a JWT token.
    """
    try:
        decrypted = jwe.deserialize_compact(token, key)
        return json.loads(decrypted["payload"].decode())
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None
    
