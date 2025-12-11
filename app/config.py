import hashlib
from  app.utils.validators import Validators

class Config:
    SECRET_KEY=""
    _KEY_ = hashlib.sha256(SECRET_KEY.encode()).digest()
    __secret_path__ ='c:/secrets/CTRLPlayer'
    __OU__ = []
    __env__=""
    __file_path__="2A3BD56F-2227-42BD-9378-32EA031982F8.json"
    __database__=""
    __database_phrase__=""
    __selected_uo__=''
    
    @staticmethod
    def getconf():
        sk_list=[]
        sk_env_list=[]
        with open(f'{Config.__secret_path__}/{Config.__file_path__}', 'r') as fh:
            for line in fh:
                sk_list.append(line.strip())
            Config.__env__=sk_list[1]
            Config.SECRET_KEY=sk_list[2]
            Config.__database_phrase__=sk_list[3]
        
        with open(f'{Config.__secret_path__}_{Config.__env__}/{Config.__file_path__}', 'r') as fh:
            for line in fh:
                sk_env_list.append(line.strip())
            Config.__database__=f"mssql+pymssql://{Validators.decrypt(sk_env_list[2],Config.__database_phrase__)}"