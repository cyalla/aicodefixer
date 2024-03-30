import os
import re 
import requests
import subprocess
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def monitor_logs():
    catalina_dir = '/scratch/cyalla/stage/apache-tomcat-9.0.87/logs'
    
    command = f'tail -n 0 -f {catalina_dir}/catalina.out'

    while True:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        try:
            buffer = []
            while True:
                line = process.stdout.readline()
                if re.search(r'^.*Exception:', line):
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
        # time.sleep(1)


def trigger_devagent_api(exception_details, className, methodName, lineNo):
    #TODO
    exception_details = clean_exception_details(exception_details)
    
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
    old_war_dir = '/scratch/cyalla/stage/apache-tomcat-9.0.87/webapps/'
    command = f'cp {new_war_dir}/app.war {old_war_dir}'

    os.system(command)


def extract_insights_from_log(exception_details):
    insights = ""

    match = re.search(r"com\.product\.controller\.(?P<ClassName>\w+)\.(?P<MethodName>\w+)\((?P<FileName>\w+)\.java:(?P<LineNumber>\d+)\)", exception_details)
    if match:
        class_name = match.group("ClassName")
        method_name = match.group("MethodName")
        file_name = match.group("FileName")
        line_number = match.group("LineNumber")

    # Extract className, methodName, and lineNo from exception_details
    pattern = r"at ([\w\.]+)\.([\w\$]+)\(([\w\.]+)\.java:(\d+)\)"
    match = re.search(pattern, exception_details)

    if match:
        className, methodName, fileName, lineNo = match.groups()
        insights = f"Class: {className}, Method: {methodName}, File: {fileName}, Line: {lineNo}"
        className = className.split(".")[-1]
    return className, methodName, lineNo


def clean_exception_details(exception_details):
    lines = exception_details.split("\n")
    exception_message = lines[0]
    stack_trace = "\n".join([line.strip() for line in lines[1:]])
    cleaned_details = f"{exception_message}\n{stack_trace}"
    return cleaned_details