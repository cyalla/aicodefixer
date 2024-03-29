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
        logging.error("First loop")

        try:
            buffer = []
            while True:
                logging.error("Second loop")
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
        trigger_devagent_api(exception_details)

        # Wait for a while before restarting the loop
        time.sleep(1)



#TODO
def trigger_devagent_api(exception_details):
    api_url = 'http://localhost:8080/api/trigger'

    payload = {
        'exception_details': exception_details
    }

    response = requests.post(api_url, json=payload)

    dir_value = response.json().get('dir')

    # Check the response status
    if response.status_code == 200:
        patch_binary_tomcat(dir_value)
    else:
        logging.error(f"Failed to trigger API. Status code: {response.status_code}")



#TODO
def patch_binary_tomcat(new_war_dir):
    old_war_dir = '/dir/to/'
    command = f'cp {new_war_dir}/app.war {old_war_dir}'

    os.system(command)
