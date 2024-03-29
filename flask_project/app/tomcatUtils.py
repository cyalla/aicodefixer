import os
import re 
import requests
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def monitor_logs():
    catalina_dir = '/path/to/tomcat/logs'  #TODO
    
    command = f'tail -n 0 -f {catalina_dir}/catalina.out'

    while True:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        try:
            buffer = []
            while True:
                line = process.stdout.readline()
                if re.search(r'^java.*Exception:', line):
                    logging.info(f"Exception detected: {line.strip()}")
                    buffer.append(line)
                    for _ in range(15):
                        buffered_line = process.stdout.readline()
                        logging.debug(f"Buffered line: {buffered_line.strip()}")
                        buffer.append(buffered_line)
                    break
        except KeyboardInterrupt:
            pass
        finally:
            process.terminate()
            process.wait()

        exception_details = "".join(buffer)

        # Trigger Spring Boot API - patch service
        className, methodName, lineNo = extract_insights_from_log(exception_details)
        trigger_devagent_api(exception_details, className, methodName, lineNo)

        # Wait for a while before restarting the loop
        time.sleep(1)


def trigger_devagent_api(exception_details, className, methodName, lineNo):
    #TODO
    api_url = 'phoenix379618.private4.oaceng02phx.oraclevcn.com/v1/postErrors'

    payload = {
        'exception_details': exception_details,
        'className': className,
        'methodName': methodName,
        'lineNo': lineNo
    }

    response = requests.post(api_url, json=payload)

    dir_value = response.json().get('dir')

    # Check the response status
    if response.status_code == 200:
        patch_binary_tomcat(dir_value)
    else:
        logging.error(f"Failed to trigger API. Status code: {response.status_code}")


def patch_binary_tomcat(new_war_dir):
    old_war_dir = '/dir/to/'
    command = f'cp {new_war_dir}/app.war {old_war_dir}'

    os.system(command)


def extract_insights_from_log(exception_details):
    insights = ""

    # Extract className, methodName, and lineNo from exception_details
    pattern = r"at ([\w\.]+)\.([\w\$]+)\(([\w\.]+)\.java:(\d+)\)"
    match = re.search(pattern, exception_details)

    if match:
        className, methodName, fileName, lineNo = match.groups()
        insights = f"Class: {className}, Method: {methodName}, File: {fileName}, Line: {lineNo}"
        className = className.split(".")[-1]
    return className, methodName, lineNo

