import jwt
import json
import datetime
# import ldap3
import subprocess
from ldap3 import Server, Connection, ALL, NTLM,MODIFY_REPLACE,SASL, GSSAPI
from app.config import Config as app_config
from app.exceptions.custom_exceptions import UserNotFoundException,UserADNoUpdatedException,UserEmpIDInUseException
from app.utils.helpers import  error_response,success_response
# from app.models.user import User

class UserService:
    
    @staticmethod    
    def validate_users(payload):
        user = json.loads(json.dumps(payload))
        
        commands = {
        "UserAD":"""
            $sam = "@@@username@@@"
            Get-ADUser -Filter { SamAccountName -eq $sam } -Properties EmployeeId, Name | Select-Object Name, SamAccountName, EmployeeID | ConvertTo-Json -Depth 2
        """
    }   
        results = {}
        for name, ps_script in commands.items():
            ps_script = (
                ps_script.replace("@@@username@@@",user['username'])
            )
            results[name] = subprocess.run(
                ["powershell", "-Command", ps_script], capture_output=True, text=True
            ) 
            if results[name].returncode != 0:
                results[name] = f"Error: {results[name].stderr.strip()}"
            else:
                if(results[name]['Name'].strip() == user['fullname'] and results[name]['SamAccountName']==user['username']):                
                    results[name] = results[name].stdout.strip()
                else:
                    results[name] = {"Error": f"the Entra Name does not match with with the provided {results[name]['Name']}", "code":401}                        
                
        return  results
        
    @staticmethod    
    def validate_users_odl(payload):
        
        user = json.loads(json.dumps(payload))
        # Conexión usando autenticación integrada (Kerberos)
        server = Server(app_config.__PPUBLIC_DOMAIN__, get_info=ALL)
        conn = Connection(server, authentication=SASL, sasl_mechanism=GSSAPI, auto_bind=True)
        print("Conexión exitosa:", conn.bound)
        
        try:
            search_filter = f'sAMAccountName={user['username']}'
            conn.search(f'dc={app_config.__PPUBLIC_DOMAIN__.split(".")[0]},dc={app_config.__PPUBLIC_DOMAIN__.split(".")[1]}',search_filter, attributes=['employeeID', 'displayName'])
                    
            if not conn.entries:
                raise UserNotFoundException("User not found")
            if len(conn.entries) == 0:
                raise UserNotFoundException("User not found")
            
            user_entry =conn.entries[0]
            current_employee_id = user_entry.employeeID.value if user_entry.employeeID else "No definido"
            
            user_data = {
                "username": user_entry.sAMAccountName.value,
                "fullname": user_entry.displayname.value,
                "employeeID": current_employee_id
            }
            
        except UserNotFoundException as e:
            return {"Error":str(e.message), "code":401} # error_response(str(e.message),401)
        except Exception as e:
            return {"Error":str(e), "code":500} #error_response(f"validating user: {str(e)}",500)
        finally:
            conn.unbind()
        
        return user_data #success_response(user_data, f'employeeID: {current_employee_id}')
    
    @staticmethod
    def modify_user(payload):
        
        # Conexión usando autenticación integrada (Kerberos/NTLM)
        server = Server(app_config.__PPUBLIC_DOMAIN__, get_info=ALL)
        conn = Connection(server, authentication=SASL, sasl_mechanism=GSSAPI, auto_bind=True)
        
        user = json.loads(json.dumps(payload))
        try:
            search_filter = f'sAMAccountName={user['username']}'
            conn.search(f'dc={app_config.__PPUBLIC_DOMAIN__.split(".")[0]},dc={app_config.__PPUBLIC_DOMAIN__.split(".")[1]}',search_filter, attributes=['employeeID', 'displayName'])
            
            if not conn.entries:
                raise UserNotFoundException("User not found")
            if len(conn.entries) == 0:
                raise UserNotFoundException("User not found")
                
            user_entry = conn.entries[0]
            user_dn = user_entry.entry_dn
                
            check_filter = f'(employeeID={user['employeeID']})'
            conn.search(f'dc={app_config.__PPUBLIC_DOMAIN__.split(".")[0]},dc={app_config.__PPUBLIC_DOMAIN__.split(".")[1]}', check_filter, attributes=['sAMAccountName'])
            
            if len(conn.entries) > 0 and conn.entries[0].entry_dn != user_dn:
                raise UserEmpIDInUseException(user_dn['description'].value)
            
            changes = {'employeeID': [(MODIFY_REPLACE, [str(user['employeeID'])])]}
            conn.modify(user_dn, changes)
            
            if conn.result['result'] != 0:
                raise UserADNoUpdatedException(f'Error: {conn.result['description']}')            
            
            user_data = {
                "username": user_entry.sAMAccountName.value,
                "fullname": user_entry.displayname.value,
                "employeeID": user['employeeID']
            }
        
        except UserEmpIDInUseException as e:
            return error_response(str(e.message),409)
        except UserNotFoundException as e:
            return error_response(str(e.message),404)
        except UserADNoUpdatedException as e:
            return error_response(str(e.message),304)
        except Exception as e:
            return error_response(f"modifying user: {str(e)}",500)
        finally:
            conn.unbind()
            
        return success_response(user_data)
