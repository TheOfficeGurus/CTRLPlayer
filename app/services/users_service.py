import json
import subprocess
from app.config import Config as app_config
from app.exceptions.custom_exceptions import UserNotFoundException,UserADNoUpdatedException,UserEmpIDInUseException
from app.utils.helpers import  error_response,success_response
# from app.models.user import User

class UserService:
    
    @staticmethod    
    def validate_users(payload):
        user = json.loads(json.dumps(payload))
        
        commands = {
        "VerifyUserAD":"""
            $sam = "@@@username@@@"
            Get-ADUser -Filter { SamAccountName -eq $sam } @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object Name, SamAccountName, EmployeeID | ConvertTo-Json -Depth 2
        """
        }   
        results = {}
        for name, ps_script in commands.items():
            ps_script = (
                ps_script.replace("@@@username@@@",user['username'])
            )
            ps_script = (
                ps_script.replace("@@@_searchbase_@@@",app_config.__OU__)
            )
            prc = subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, text=True
            ) 
            if prc.returncode != 0:
                results[name] = f"Error: {prc.stderr.strip()}"
                continue
            
            
            try:
                data = json.loads(prc.stdout) 
            except json.JSONDecodeError:
                results[name] = {"Error": "Invalid JSON output", "code": 500}
                continue
                
            if data.get('Name', '').strip() == user['fullname'] and data.get('SamAccountName') == user['username']:
                results[name] = prc.stdout.strip()
            else:
                results[name] = {
            "Error": f"the Entra Name does not match with the provided {data.get('Name')}",
            "code": 401
            }   
        
        return  results
        
    @staticmethod    
    def validate_users_odl(payload):
        
        user = json.loads(json.dumps(payload))
        try:
            user_data = {
                "username": user['username'],
                "fullname": user['fullname'],
                "employeeID": user['employeeId']
            }
            
        except UserNotFoundException as e:
            return {"Error":str(e.message), "code":401} # error_response(str(e.message),401)
        except Exception as e:
            return {"Error":str(e), "code":500} #error_response(f"validating user: {str(e)}",500)
        # finally:
            # conn.unbind()
        
        return user_data #success_response(user_data, f'employeeID: {current_employee_id}')
    
    @staticmethod
    def modify_user(payload):
        
        user = json.loads(json.dumps(payload))
        try:
            user_data = {
                "username": user['username'],
                "fullname": user['fullname'],
                "employeeID": user['employeeId']
            }
        except UserEmpIDInUseException as e:
            return error_response(str(e.message),409)
        except UserNotFoundException as e:
            return error_response(str(e.message),404)
        except UserADNoUpdatedException as e:
            return error_response(str(e.message),304)
        except Exception as e:
            return error_response(f"modifying user: {str(e)}",500)
        # finally:
        #     conn.unbind()
            
        return success_response(user_data)
