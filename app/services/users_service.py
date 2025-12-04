import json
import subprocess
from app.config import Config as app_config
from app.exceptions.custom_exceptions import APIException, UserNotFoundException,UserADNoUpdatedException,UserEmpIDInUseException
from app.utils.helpers import  error_response
from app.models.employeeChangeLog import EmployeeChangeLog as dbEmpLog
from app.models.base import db

class UserService:
    @staticmethod    
    def validate_username(payload):
        user = json.loads(json.dumps(payload))
        
        commands = {
        "VerifyUserAD":""" Get-ADUser -Filter { SamAccountName -eq '@@@username@@@' } -SearchBase  @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object @{Name='fullname';Expression={$_.Name}}, @{Name='username';Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """
        }   
        results = {}
        for name, ps_script in commands.items():
            ps_script = (
                ps_script.replace("@@@username@@@",user['username'])
            )
            ps_script = (
                ps_script.replace("@@@_searchbase_@@@",app_config.__selected_uo__)
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
            "Error": f"the Entra name does not match with the provided {data.get('Name')}",
            "code": 401
            }   
        
        return  results
    @staticmethod    
    def validate_fullname(payload):
        user = json.loads(json.dumps(payload))
        results = {}
        data={'fullname':'Nil'}
        command =''
        for uo in app_config.__OU__:
            command =""" Get-ADUser -Filter { Name -eq '@@@fullname@@@' } -SearchBase '@@@_searchbase_@@@'-Properties EmployeeId, Name | Select-Object @{Name='fullname';Expression={$_.Name}}, @{Name='username';Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """
            command = command.replace("@@@fullname@@@",user['fullname'])
            command= command.replace("@@@_searchbase_@@@",uo)        
            prc = subprocess.run(
                ["powershell", "-Command", command.strip()], capture_output=True, text=True
            ) 
            if prc.returncode != 0:
                results['Employee'] = f"Error: {prc.stderr.strip()}"
            else:
                try:
                    data = json.loads(prc.stdout) 
                    app_config.__selected_uo__ = uo
                    break
                except json.JSONDecodeError:
                    results['Employee'] = {"Error": "Invalid JSON output", "code": 500}
        
        try:
            if data.get('fullname').strip() == user['fullname'].strip() :
                results['Employee'] = data
            else:
                results['Employee'] = {
            "Error": f"the Entra name does not match with the provided {data.get('Name')}",
            "code": 401
            }
                raise Exception(results)
        except json.JSONDecodeError:
            results['Employee'] = {"Error": "Invalid JSON output", "code": 500}
        # except Exception as e:
        #     # err = str(e)
        #     results['Employee'] = {"Error": f"{str(e)}", "code": 500}
        return  results    
    
    @staticmethod    
    def validate_empid(payload):
        empid = json.loads(json.dumps(payload))
        data = {'fullname':'Nill'}
        commands =""" Get-ADUser -Filter { EmployeeId -eq "@@@_EmpID_@@@" } -SearchBase "@@@_searchbase_@@@" -Properties EmployeeId, Name | Select-Object @{Name="fullname";Expression={$_.Name}}, @{Name="username";Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """
        
        results = {}
        # for name, ps_script in commands.items():
        for ou in app_config.__OU__:
            commands = commands.replace("@@@_EmpID_@@@", empid['EmployeeID'])
            commands = commands.replace("@@@_searchbase_@@@",ou)
            prc = subprocess.run(
                ["powershell", "-Command", commands.strip()], capture_output=True, text=True
            ) 
            if prc.returncode != 0:
                results['EmployeeInfo'] = f"Error: {prc.stderr.strip()}"
                continue
                # raise APIException(results['EmployeeInfo'],500) 
            else: 
                try:
                    data = json.loads(prc.stdout)                     
                    results['EmployeeInfo'] = data
                    break
                except json.JSONDecodeError:
                    results['EmployeeInfo'] = {"Error": "Invalid JSON output", "code": 500}
                    continue
        try:
            if data.get('EmployeeID').strip() == empid['EmployeeID'].strip() :
                results['EmployeeInfo'] = data
            else:
                results['EmployeeInfo'] = {
            "Error": f"the Entra name does not match with the provided {data.get('Name')}",
            "code": 401
            }
                raise Exception(results)
        except json.JSONDecodeError:
            results['EmployeeInfo'] = {"Error": "Invalid JSON output", "code": 500}
        
        return  results    
    
    @staticmethod
    def exists_empId(empid:str) -> bool:
        pwsh_command= """[bool](Get-ADUser -Filter { EmployeeId -eq "@@@_EmpID_@@@" } -SearchBase @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object EmployeeID ) """
        pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",app_config.__selected_uo__)
        pwsh_command = pwsh_command.replace("@@@_EmpID_@@@", empid)
        prc = subprocess.run(
                        ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
                    )
        return prc.stdout.strip().lower() == "true"
    
    @staticmethod
    def exists_FullEmployee_username(username:str) -> bool:
        pwsh_command= """[bool]( Get-ADUser -Filter { SamAccountName -eq '@@@username@@@' } -SearchBase @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object Name, SamAccountName, EmployeeID) """
        pwsh_command = pwsh_command.replace("@@@username@@@",username)
        pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",app_config.__selected_uo__)
        prc = subprocess.run(
                        ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
                    )
        return prc.stdout.strip().lower() == "true"
    
    @staticmethod
    def get_employee_general_info_username(username:str):
        pwsh_command =""" Get-ADUser -Filter { SamAccountName -eq '@@@username@@@' } -SearchBase @@@_searchbase_@@@ -Properties EmployeeId, Name | Select-Object @{Name='fullname';Expression={$_.Name}}, @{Name='username';Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """            
        data =""
        pwsh_command = pwsh_command.replace('@@@username@@@',username)
        pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",app_config.__selected_uo__)
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
            
            if not UserService.exists_FullEmployee_username(usr_pay['username']):
                raise UserNotFoundException(f"This username `{usr_pay['username']}` does not exists or you don have access to the OU folder")
            
            if UserService.exists_empId(usr_pay['employeeId']):
                raise UserEmpIDInUseException(f"This EmployeeId {usr_pay['employeeId']} is been used by other employee")
            
            data = UserService.get_employee_general_info_username(usr_pay['username'])

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
            data = UserService.get_employee_general_info_username(usr_pay['username'])
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
