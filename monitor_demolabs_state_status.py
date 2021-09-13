import argparse
import sys

import mysql.connector
from mysql.connector import Error
from Vm_Stats_Handler import *
import requests

#####################################
######### Globals variables #########
#####################################


######## thresholds #########
#############################
cpu_threshold = 70
memory_threshold = 80
labs_count_threshold = 25

#############################
# portal DB connection data #
#############################
# portal_ip = None
# portal_db_name = None
# portal_usr = None
# portal_pass = None
############################


## prtg connection data ####
############################
# prtg_connect_data = dict(host=portal_ip,
#                     database=portal_db_name,
#                     user=portal_usr,
#                     password=portal_pass)
#prtg_connect_data = ('portal_ip', 'portal_db_name', 'portal_usr', 'portal_pass')


#### prtg sensors data #####
############################
# id of target device for testing
target_device_Germany = "2909"
target_device_NJ = "2019"
# set tag of target devices
target_tag_Germany = "vmtomonitorGermany"
target_tag_NJ = "vmtomonitorNJ"
# temporary data dictionary
prtg_vms_count = {}
############################


######## time data #########
############################
#cur_time =
############################

# getarg to add later
# def GetArgs():
#    """
#    Supports the command-line arguments listed below.
#    """
#    parser = argparse.ArgumentParser(
#        description='Process args for retrieving all the Virtual Machines')
#    parser.add_argument('-s', '--host', required=True, action='store',
#                        help='Remote host to connect to')
#    parser.add_argument('-o', '--port', type=int, default=443, action='store',
#                        help='Port to connect on')
#    parser.add_argument('-u', '--user', required=True, action='store',
#                        help='User name to use when connecting to host')
#    parser.add_argument('-v', '--vm', required=True, action='store',
#                        help='header vm to monitor')
#    parser.add_argument('-p', '--password', required=False, action='store',
#                        help='Password to use when connecting to host')
#    args = parser.parse_args()
#    return args

# established connection to required DB and return cursor
def get_db_cursor(host, db, user, password):
    try:
        connection = mysql.connector.connect(host=host,
                                             database=db,
                                             user=user,
                                             password=password)

        if connection.is_connected():
            return connection.cursor()
        else:
            return 0

    except Error as e:
        print("Error while connecting to MySQL", e)


# established connection to portal db, query count of active labs and return total labs count
def get_portal_db_data():
    try:
        # established connection to DB
        connection = mysql.connector.connect(**prtg_connect_data)
        if connection.is_connected():
            # open DB cursor
            cursor = connection.cursor()

            # Query number of labs categorized by lab type
            cursor.execute(
                "SELECT Lab, COUNT(VMName) FROM Reservations WHERE End >= UTC_TIMESTAMP() AND RDP IS NOT NULL GROUP BY Lab;")
            record = cursor.fetchall()
            # convert result to dict
            reservations_vm_lst = dict(record)

            return reservations_vm_lst

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


def hardware_data_from_prtg(target_tag):
    connect_keys_str = "http://" + prtg_ip + "/api/"
    auth_keys_str = "&username=" + prtg_usr + "&password=" + prtg_pass

    # get all sensors with the given target tag
    device_response = requests.get(
        connect_keys_str + "table.json?content=sensors&columns=objid,name,device&count=*&filter_tags=" + target_tag + auth_keys_str)

    # list of vm's scanned for fixing calculating age issue
    vms_scanned_list = []

    if str(device_response) == "<Response [200]>":  # check successful connection to prtg server
        # iterate over all sensors and get channels last values
        for sensorId in device_response.json()["sensors"]:
            # get lab name from sensor
            device_response = requests.get(
                connect_keys_str + "getsensordetails.json?content=channels&output=json&columns=name,lastvalue&id=" + sensorId + auth_keys_str)
            sensor_name = str(device_response.json()["sensordata"]["name"]).split("-")[0]
            data_type = str(device_response.json()["sensordata"]["name"]).split("-")[2]
            if sensor_name not in vms_scanned_list:
                vms_scanned_list.append(sensor_name)

                # get sensor last channels last values
                device_response = requests.get(
                    connect_keys_str + "table.json?content=channels&output=json&columns=name,lastvalue&id=" + sensorId + auth_keys_str)
                for channel in device_response["channels"]:
                    if channel["lastvalue_raw"] > 0.05: # check if lab is active
                        channel["name"]







if __name__ == '__main__':
    # get arguments
    args = sys.argv[1:]
    portal_ip = args[0]
    portal_db_name = args[1]
    portal_usr = args[2]
    portal_pass = args[3]
    prtg_ip = args[4]
    prtg_usr = args[5]
    prtg_pass = args[6]

    # portal DB connection data
    prtg_connect_data = dict(host=portal_ip,
                             database=portal_db_name,
                             user=portal_usr,
                             password=portal_pass)

    print(get_portal_db_data())



