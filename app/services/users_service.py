from datetime import date
import json
import os
import subprocess
import re
from app.config import Config as app_config
from app.exceptions.custom_exceptions import APIException, UserNotFoundException,UserADNoUpdatedException,UserEmpIDInUseException
from app.utils.helpers import  error_response
from app.models.employeeChangeLog import EmployeeChangeLog as dbEmpLog
from app.models.base import db
import logging
class UserService:
    basefile = os.path.abspath(__file__)
    basepath = os.path.dirname(basefile)
    log_file:str = basepath+'\\Log\\'+'ctrlPlayer_'+str(date.today())+'.log'
    logging.basicConfig(level=logging.DEBUG,format='%(asctime)s - %(levelname)s - %(message)s',filename=log_file, filemode='a')
    
    # @staticmethod    
    # def validate_username(payload):
    #     user = json.loads(json.dumps(payload))
    #     data = {'username':'Nill'}
    #     commands = {
    #     "VerifyUserAD":""" Get-ADUser -Filter { SamAccountName -eq '@@@username@@@' } -SearchBase  "@@@_searchbase_@@@" -Properties EmployeeId, Name | Select-Object @{Name='fullname';Expression={$_.Name}}, @{Name='username';Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """
    #     }   
    #     results = {}
    #     for name, ps_script in commands.items():
    #         for uo in app_config.__OU__:
    #             ps_script = (
    #                 ps_script.replace("@@@username@@@",user['username'])
    #             )
    #             ps_script = (
    #                 ps_script.replace("@@@_searchbase_@@@",uo)
    #             )
    #             prc = subprocess.run(
    #                 ["powershell", "-Command", ps_script.strip()], capture_output=True, text=True
    #             ) 
    #             if prc.returncode != 0:
    #                 results[name] = f"Error: {prc.stderr.strip()}"
    #                 continue            
                
    #             try:
    #                 data = json.loads(prc.stdout) 
    #             except json.JSONDecodeError:
    #                 results[name] = {"Error": "Invalid JSON output", "code": 500}
    #                 continue
    #         if data:
    #             if data.get('fullname').strip() == user['fullname'].strip() and data.get('username').strip() == user['username'].strip():
    #                 results[name] = data
    #         else:
    #             results[name] = {
    #         "Error": f"the Entra name does not match with the provided {data.get('Name')}",
    #         "code": 401
    #         }   
        
    #     return  results
    @staticmethod    
    def validate_fullname(payload):
        user = json.loads(json.dumps(payload))
        results = {}
        data={'fullname':'Nil'}
        command =''
        for uo in app_config.__OU__:
            command =""" Get-ADUser -Filter { Name -eq '@@@fullname@@@' } -SearchBase "@@@_searchbase_@@@" -Properties EmployeeId, Name | Select-Object @{Name='fullname';Expression={$_.Name}}, @{Name='username';Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """
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
            if data.get('fullname').strip() == user['fullname'].strip() : # type: ignore
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
            if data.get('EmployeeID').strip() == empid['EmployeeID'].strip() : # type: ignore
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
        for uo in app_config.__OU__:
            pwsh_command= """[bool](Get-ADUser -Filter { EmployeeId -eq "@@@_EmpID_@@@" } -SearchBase "@@@_searchbase_@@@" -Properties EmployeeId, Name | Select-Object EmployeeID ) """
            pwsh_command = pwsh_command.replace("@@@_searchbase_@@@", uo)
            pwsh_command = pwsh_command.replace("@@@_EmpID_@@@", empid)
            prc = subprocess.run(
                            ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
                        )
            if prc.stdout.strip().lower() == "true":
                return True
        return False
    
    @staticmethod
    def exists_FullEmployee_username(username:str) -> bool:
        for uo in app_config.__OU__:
            pwsh_command= """[bool]( Get-ADUser -Filter { SamAccountName -eq "@@@username@@@" } -SearchBase "@@@_searchbase_@@@" -Properties EmployeeId, Name | Select-Object Name, SamAccountName, EmployeeID) """
            pwsh_command = pwsh_command.replace("@@@username@@@",username)
            pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",uo)
            prc = subprocess.run(
                            ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
                        )            
            if prc.stdout.strip().lower() == "true":
                return True
        return False
    
    @staticmethod
    def get_employee_general_info_username(username:str):
        result =''
        for uo in app_config.__OU__:
            pwsh_command =""" Get-ADUser -Filter { SamAccountName -eq "@@@username@@@" } -SearchBase "@@@_searchbase_@@@" -Properties EmployeeId, Name | Select-Object @{Name="fullname";Expression={$_.Name}}, @{Name="username";Expression={$_.SamAccountName}}, EmployeeID | ConvertTo-Json -Depth 2 """            
            pwsh_command = pwsh_command.replace('@@@username@@@',username)
            pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",uo)
            prc = subprocess.run(
                ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
                ) 
            if prc.returncode != 0:
                result = f"{prc.stderr.strip()}"
                continue
            else:
                return json.loads(prc.stdout.strip()) 
        if result:
            raise UserADNoUpdatedException(result)
    
    @staticmethod
    def get_employee_general_info_employeeid(employeeId:str):
        result =''
        for uo in app_config.__OU__:
            pwsh_command =""" Get-ADUser -Filter { EmployeeID -eq "@@@username@@@" } -SearchBase "@@@_searchbase_@@@" -Properties EmployeeId, Name, Manager | Select-Object @{Name="fullname";Expression={$_.Name}}, @{Name="username";Expression={$_.SamAccountName}}, EmployeeID, Manager | ConvertTo-Json -Depth 2 """            
            pwsh_command = pwsh_command.replace('@@@username@@@',employeeId)
            pwsh_command = pwsh_command.replace("@@@_searchbase_@@@",uo)
            prc = subprocess.run(
                ["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True
                ) 
            if prc.returncode != 0:
                result = f"{prc.stderr.strip()}"
                continue
            else:
                return json.loads(json.dumps(prc.stdout))
        if result:
            raise UserADNoUpdatedException(result)
    
    @staticmethod    
    def modify_user(payload):
        results ={}
        
        #validate if empID is inUse
        try:
            usr_pay=  json.loads(json.dumps(payload))
            results = {}
            
            if not UserService.exists_FullEmployee_username(usr_pay['username']):
                raise UserNotFoundException(f"This username `{usr_pay['username']}` does not exists or you dont have access to the OU folder")
            
            if UserService.exists_empId(usr_pay['employeeId']):
                raise UserEmpIDInUseException(f"This EmployeeId {usr_pay['employeeId']} is been used by other employee")
            
            data = UserService.get_employee_general_info_username(usr_pay['username'])
            if data:
                if not dbEmpLog.find_by_username(usr_pay['username']):
                    employee = dbEmpLog(data.get('username').strip(),data.get('EmployeeID').strip(),data.get('fullname').strip(),'sys','base info before change')
                    # employee = dbEmpLog(usr_pay['username'],usr_pay['employeeId'].strip(),usr_pay['fullname'],'sys','base info before change')
                    employee.save()
                
            #replace EmpID            
            pwsh_command = """ Set-ADUser -Identity "@@@username@@@" -Replace @{employeeId="@@@_EmpID_@@@"} """
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
            if data:
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

    @staticmethod
    def assing_New_Supervisor(payload):
        results ={}
        try:
            usr = json.loads(json.dumps(payload))
            
            if not UserService.exists_empId(usr['sup_employeeID']):
                raise UserNotFoundException(f"This supervisor badge number does not exists, is inactive or is out of context:  {usr['sup_employeeID']} ")
            
            if not UserService.exists_empId(usr['guru_employeeID']):
                raise UserNotFoundException(f"This guru badge number does not exists, is inactive or is out of context:  {usr['guru_employeeID']} ")
            
            sup_location = UserService.get_distinguishedName (usr['sup_employeeID'])
            guru_data = json.loads(UserService.get_employee_general_info_employeeid(usr['guru_employeeID'])) # type: ignore
            
            if guru_data:
                if not dbEmpLog.find_by_username(guru_data['username']):
                    employee = dbEmpLog(guru_data.get('username').strip(),guru_data.get('EmployeeID').strip(),guru_data.get('fullname').strip(),'sys','base info before change')
                    employee.save()
                
                pwsh_command = """ Set-ADUser -Identity "@@@username@@@" -Replace @{Manager="@@@sup_Loc@@@"} """
                pwsh_command = pwsh_command.replace('@@@username@@@',guru_data['username'])
                pwsh_command = pwsh_command.replace('@@@sup_Loc@@@',sup_location)
                prc = subprocess.run(["powershell", "-Command", pwsh_command.strip()], capture_output=True, text=True)
                
                if prc.returncode != 0:
                    raise UserADNoUpdatedException (f"Error: {prc.stderr.strip()}")
                
                results['Assigned'] = UserService.exists_empId(usr['guru_employeeID'])
                
                #Validate changes
                data = json.loads(UserService.get_employee_general_info_employeeid(usr['guru_employeeID'])) # type: ignore
                if data:
                    if data['EmployeeID'].strip() == usr['guru_employeeID'].strip():
                        match = re.search(r"CN=([^,]+)", data['Manager'], re.IGNORECASE)
                        data['Manager'] = match.group(1).strip() if match else None
                        results['Employee'] = data
                        
                        employee = dbEmpLog(username=data['username'],employeeId=data['EmployeeID'],full_name=data['fullname'],updated_by=usr['updatedBy'],change_desc=f'new supervisor assigned {data['Manager']} ')
                        employee.save()
                
        except json.JSONDecodeError:
            results['Error'] = "Error Invalid JSON output"
        except UserNotFoundException as r :
            results['Error']=f"{r.message}"
        except UserADNoUpdatedException as e:
            results['Error']=f"{e.message}"
        except Exception as e:
            results['Error']=f"assignSupervidor: {str(e)}"
        finally:
            return results

    @staticmethod
    def get_distinguishedName(employeeId:str):
        result = None
        for uo in app_config.__OU__:
            pwsh_command = """ Get-ADUser -Filter { EmployeeId -eq "@@@_EmpID_@@@" } -SearchBase "@@@_searchbase_@@@" | Select-Object DistinguishedName | ConvertTo-Json -Depth 2 """
            pwsh_command = pwsh_command.replace("@@@_searchbase_@@@", uo)
            pwsh_command = pwsh_command.replace("@@@_EmpID_@@@", employeeId)
            
            prc = subprocess.run(
                ["powershell", "-Command", pwsh_command.strip()],
                capture_output=True,
                text=True
            )

            if prc.returncode != 0:
                result = prc.stderr
                continue
        
            if prc.stdout:            
                data = json.loads(prc.stdout)
                
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                
                dn = data.get("DistinguishedName") # type: ignore
                if dn and dn.startswith("CN="):
                    return dn

        raise UserNotFoundException(result)
