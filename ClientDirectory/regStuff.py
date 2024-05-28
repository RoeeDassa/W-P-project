import winreg
from winreg import *
from client_constants import *
from elevate import elevate

"""
Name: regStuff
Author: Roee Dassa
Explanation: file used to handle
info added / received from the registry
"""


class RegistryManager:
    @staticmethod
    def to_str(hkey_constant):
        """
        translate winreg module hkey constant
        to string for printout purposes
        """
        if hkey_constant == HKEY_CLASSES_ROOT:
            return "HKEY_CLASSES_ROOT"
        elif hkey_constant == HKEY_CURRENT_USER:
            return "HKEY_CURRENT_USER"
        elif hkey_constant == HKEY_LOCAL_MACHINE:
            return "HKEY_LOCAL_MACHINE"
        elif hkey_constant == HKEY_USERS:
            return "HKEY_USERS"
        elif hkey_constant == HKEY_CURRENT_CONFIG:
            return "HKEY_CURRENT_CONFIG"
        else:
            return None


class RegistrySetter(RegistryManager):
    @staticmethod
    def create_reg(data):
        """
        Save the data (the UserName) in the registry
        under HKEY_LOCAL_MACHINE\SOFTWARE\CVSM
        """
        location = winreg.HKEY_LOCAL_MACHINE
        access = winreg.KEY_WRITE
        with winreg.OpenKey(location, path, 0, access) as registry_key:
            winreg.SetValueEx(registry_key, value_name, 0, winreg.REG_SZ,
                              data)

    @staticmethod
    def create_running_reg(data):
        """
        Save the start_pServer.bat file in the registry under
        HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
        """
        location = winreg.HKEY_CURRENT_USER
        access = winreg.KEY_WRITE
        with winreg.OpenKey(location, batch_path, 0, access) as registry_key:
            winreg.SetValueEx(registry_key, batch_name, 0, winreg.REG_SZ,
                              data)


class RegistryGetter(RegistryManager):
    @staticmethod
    def get_reg(root, path, name):
        """
        prints the value of given registry entry root\path\value
        creates it if does not exist
        """
        try:
            registry_key = OpenKey(root, path, 0, KEY_READ)
            value, regtype = QueryValueEx(registry_key, name)
            CloseKey(registry_key)
            print(value)
        except WindowsError as e:
            print("get_reg: ", e)



def main():
    """
    tests read registry key
    """
    RegistryGetter.get_reg(HKEY_CURRENT_USER,
                           r"Control Panel\Mouse", 'MouseSensitivity')

    RegistrySetter.set_reg(HKEY_CURRENT_USER,
                           r"Control Panel\Mouse", 'MouseSensitivity', '10')


if __name__ == '__main__':
    main()
