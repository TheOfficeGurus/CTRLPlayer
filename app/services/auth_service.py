import jwt
import json
import datetime
# from app.models.user import User
from app.config import Config as app_config
from authlib.jose import JsonWebEncryption as jwe
from app.exceptions.custom_exceptions import TokenClaimsMismatch

class AuthService:    
    
    @staticmethod
    def LoadConfigs(pajsonyload):
        sk_list= []
        conf=[]
        services=[]
        conf_json = json.loads(json.dumps(pajsonyload))
        service = conf_json['service']
        environment = conf_json['environment']
        phrase = conf_json['phrase']
        
        
        with open(f'{app_config.__secret_path__}_{environment}/2A3BD56F-2227-42BD-9378-32EA031982F8.json', 'r') as fh:
            for line in fh:
                sk_list.append(line.strip())
                
        if not phrase in sk_list or not sk_list[1]==environment:
            raise TokenClaimsMismatch()
        
        with open(f'{app_config.__secret_path__}_{environment}/services.json', 'r') as fh:
            for line in fh:
                services.append(line.strip())
                
        if not  service in services:
            raise TokenClaimsMismatch() 
            
        with open(f'{app_config.__secret_path__}_{environment}/conf.json', 'r') as fh:
            for line in fh:
                conf.append(line)
            
        if not conf:
            raise TokenClaimsMismatch()
        
        app_config.__OU__ = conf
        
    
    @staticmethod    
    def generate_token(payload):
        
        protected_header = {
            "alg": "dir",
            "enc": "A256GCM"
        }
        
        token_json = json.loads(json.dumps(payload))
        token_json['exp'] = (datetime.datetime.now(tz=datetime.timezone.utc)+ datetime.timedelta(minutes=10)).isoformat()
        token_json['iat'] = (datetime.datetime.now(tz=datetime.timezone.utc)).isoformat()
        token_json['iss'] = f'CTRLPlayer for the galaxy'
        
        jwt_json = json.dumps(token_json).encode()
        jwt_token:str = jwe().serialize_compact(protected_header, jwt_json, app_config._KEY_).__str__().replace('b\'', '').replace("'", '')
        return jwt_token
