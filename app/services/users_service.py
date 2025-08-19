import json
import subprocess
from app.config import Config as app_config
from app.exceptions.custom_exceptions import UserNotFoundException,UserADNoUpdatedException,UserEmpIDInUseException
from app.utils.helpers import  error_response
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
                ["powershell", "-Command", ps_script.strip()], capture_output=True, text=True
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
    def exists_empId(empid:str) -> bool:
        command= """[bool](Get-ADUser -Filter { EmployeeId -eq "@@@_EmpID_@@@" } @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object EmployeeID )
                """
        command = command.replace("@@@_searchbase_@@@",app_config.__OU__)
        command = command.replace("@@@_EmpID_@@@", empid)
        prc = subprocess.run(
                        ["powershell", "-Command", command.strip()], capture_output=True, text=True
                    )
        return bool(prc.stdout.strip())
    @staticmethod    
    def modify_user(payload):
        results ={}
        
        #validate if empID is inUse
        try:
            usr_pay=  json.loads(json.dumps(payload))
            
            if UserService.exists_empId(usr_pay['employeeId']):
                raise UserEmpIDInUseException(f"This EmployeeId {usr_pay['employeeId']} is been used by other employee")
                
            #replace EmpID
            if results['username']==usr_pay['username'] :
                next_comnnad = """
                $sam = "@@@username@@@"
                Set-ADUser -Identity $sam -Replace @{employeeId='@@@_EmpID_@@@'}
                """
                next_comnnad = next_comnnad.replace("@@@username@@@",usr_pay['username'])
                next_comnnad = next_comnnad.replace("@@@_EmpID_@@@",usr_pay['employeeId'])
                prc = subprocess.run(
                    ["powershell", "-Command", next_comnnad.strip()], capture_output=True, text=True
                ) 
                if prc.returncode != 0:
                    results['Employee'] = f"Error: {prc.stderr.strip()}"
                
                results['Assigned'] = UserService.exists_empId(usr_pay['employeeId'])
            
            #Validate changes
            command ="""
            Get-ADUser -Filter { SamAccountName -eq "@@@username@@@" } @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object Name, SamAccountName, EmployeeID | ConvertTo-Json -Depth 2
            """            
            results = {}
            data =""
            command.replace("@@@username@@@",usr_pay['username'])
            command.replace("@@@_searchbase_@@@",app_config.__OU__)
            prc = subprocess.run(
                ["powershell", "-Command", command.strip()], capture_output=True, text=True
                ) 
            if prc.returncode != 0:
                raise UserADNoUpdatedException(f"Message: {prc.stderr.strip()}")
            data = json.loads(prc.stdout) 
            if data.get('Name', '').strip() == usr_pay['fullname'] and data.get('SamAccountName') == usr_pay['username']:
                results['Employee'] = prc.stdout.strip()
                    
        except json.JSONDecodeError:
            results['Error'] = "Error Invalid JSON output"
            return results
        except UserEmpIDInUseException as e:
            results['Error']=f"Message: {e.message}"
            return results
        except UserNotFoundException as e:
            results['Error']=f"Message: {e.message}"
            return   results
        except UserADNoUpdatedException as e:
            results['Error']=f"Message: {e.message}"
            return results
        except Exception as e:
            results['Error']=f"modifying user: {str(e)}"
            return results
        # finally:
            # conn.unbind()
        
        return results #success_response(user_data, f'employeeID: {current_employee_id}')
    
    @staticmethod
    def validate_users_odl(payload):
        
        user = json.loads(json.dumps(payload))
        result={}
        try:
            
            val = UserService.exists_empId(user['employeeId'])
            result['response'] = f"valValue: {val}"
            result['empId'] = f"userRequest: {user['employeeId']}"
            
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
            
        return result
