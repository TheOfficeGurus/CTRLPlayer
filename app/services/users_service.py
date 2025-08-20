import json
import subprocess
from app.config import Config as app_config
from app.exceptions.custom_exceptions import UserNotFoundException,UserADNoUpdatedException,UserEmpIDInUseException
from app.utils.helpers import  error_response
from app.models.employeeChangeLog import EmployeeChangeLog as dbEmpLog
from app.models.base import db

class UserService:
    
    @staticmethod    
    def validate_users(payload):
        user = json.loads(json.dumps(payload))
        
        commands = {
        "VerifyUserAD":""" Get-ADUser -Filter { SamAccountName -eq '@@@username@@@' } @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object @{Name='fullname';Expression={$_.Name}}, @{Name='username';Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """
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
            
            if data.get('fullname').strip() == user['fullname'].strip() and data.get('username').strip() == user['username'].strip():
                results[name] = data
            else:
                results[name] = {
            "Error": f"the Entra Name does not match with the provided {data.get('Name')}",
            "code": 401
            }   
        
        return  results

    
    @staticmethod
    def exists_empId(empid:str) -> bool:
        pwsh_command= """[bool](Get-ADUser -Filter { EmployeeId -eq "@@@_EmpID_@@@" } @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object EmployeeID ) """
        pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",app_config.__OU__)
        pwsh_command = pwsh_command.replace("@@@_EmpID_@@@", empid)
        prc = subprocess.run(
                        ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
                    )
        return prc.stdout.strip().lower() == "true"
    
    @staticmethod
    def exists_FullEmployee(username:str) -> bool:
        pwsh_command= """[bool]( Get-ADUser -Filter { SamAccountName -eq '@@@username@@@' } @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object Name, SamAccountName, EmployeeID) """
        pwsh_command = pwsh_command.replace("@@@username@@@",username)
        pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",app_config.__OU__)
        prc = subprocess.run(
                        ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
                    )
        return prc.stdout.strip().lower() == "true"
    
    @staticmethod
    def get_employee_general_info(username:str):
        pwsh_command =""" Get-ADUser -Filter { SamAccountName -eq '@@@username@@@' } @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object @{Name='fullname';Expression={$_.Name}}, @{Name='username';Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """            
        data =""
        pwsh_command = pwsh_command.replace('@@@username@@@',username)
        pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",app_config.__OU__)
        prc = subprocess.run(
            ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
            ) 
        if prc.returncode != 0:
            raise UserADNoUpdatedException(f"{prc.stderr.strip()}")
        
        return json.loads(prc.stdout.strip()) 
    
    @staticmethod    
    def modify_user(payload):
        results ={}
        
        #validate if empID is inUse
        try:
            usr_pay=  json.loads(json.dumps(payload))
            results = {}
            
            if not UserService.exists_FullEmployee(usr_pay['username']):
                raise UserNotFoundException(f"This username `{usr_pay['username']}` does not exists or you don have access to the OU folder")
            
            if UserService.exists_empId(usr_pay['employeeId']):
                raise UserEmpIDInUseException(f"This EmployeeId {usr_pay['employeeId']} is been used by other employee")
            
            data = UserService.get_employee_general_info(usr_pay['username'])

            if not dbEmpLog.find_by_username(usr_pay['username']):
                employee = dbEmpLog(data.get('username').strip(),data.get('EmployeeID').strip(),data.get('fullname').strip(),'sys','base info before change')
                # employee = dbEmpLog(usr_pay['username'],usr_pay['employeeId'].strip(),usr_pay['fullname'],'sys','base info before change')
                employee.save()
                
            #replace EmpID            
            pwsh_command = """ Set-ADUser -Identity '@@@username@@@' -Replace @{employeeId='@@@_EmpID_@@@'} """
            pwsh_command = pwsh_command.replace("@@@username@@@",usr_pay['username'].strip())
            pwsh_command = pwsh_command.replace("@@@_EmpID_@@@",usr_pay['employeeId'].strip())
            prc = subprocess.run(
                ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
            ) 
            if prc.returncode != 0:
                raise UserADNoUpdatedException (f"Error: {prc.stderr.strip()}")
            
            results['Assigned'] = UserService.exists_empId(usr_pay['employeeId'])            
            
            #Validate changes
            data = UserService.get_employee_general_info(usr_pay['username'])
            if data.get('fullname').strip() == usr_pay['fullname'].strip() and data.get('username').strip() == usr_pay['username'].strip():
                results['Employee'] = data
            
            employee = dbEmpLog(usr_pay['username'],usr_pay['employeeId'],usr_pay['fullname'],usr_pay['updatedBy'],'new employee Id assignation')
            employee.save()
            
        except json.JSONDecodeError:
            results['Error'] = "Error Invalid JSON output"
            return results
        except UserEmpIDInUseException as e:
            results['Error']=f"{e.message}"
            return results
        except UserNotFoundException as e:
            results['Error']=f"{e.message}"
            return   results
        except UserADNoUpdatedException as e:
            results['Error']=f"{e.message}"
            return results
        except Exception as e:
            results['Error']=f"modifying user: {str(e)}"
            return results
            
        return results     
