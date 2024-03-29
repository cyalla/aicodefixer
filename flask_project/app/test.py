'''
IGNORE THE CODE HERE
JUST FOR TESTING PURPOSES
IS NOT A PART OF THE MAIN PROJECT
WILL BE REMOVED AFTER FINAL TESTING
'''

import re

def monitor_logs():
    catalina_dir = '/path/to/tomcat/logs'  #TODO
    error_log_file_path = '/path/to/logfile.log'

    command = f'tail -n 0 -f {catalina_dir}/catalina.out'

    while True:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        try:
            buffer = []
            while True:
                line = process.stdout.readline()
                if re.search(r'^java.*Exception:', line):
                    buffer.append(line)
                    for _ in range(15):
                        buffer.append(process.stdout.readline())
                    break
        except KeyboardInterrupt:
            pass
        finally:
            process.terminate()
            process.wait()

        # Write the buffer to the log file
        with open(error_log_file_path, 'a') as file:
            for buffered_line in buffer:
                file.write(buffered_line)

        # Extract insights and trigger Spring Boot API
        exception_details = extract_insights_from_log(error_log_file_path)
        trigger_devagent_api(exception_details)

        # Wait for a while before restarting the loop
        time.sleep(1)

# Example usage
log_file_path = '/Users/bhopsing/Desktop/Orahacks/venv/aicodefixer/flask_project/app/error.txt'
insights = extract_insights_from_log(log_file_path)
print(insights)




def extract_insights_from_log(error_log_file_path):
    insights = ""

    with open(error_log_file_path, 'r') as file:
        lines = file.readlines()

        for line in lines: 

            line = line.strip()

            if re.match(r"java\.lang\..+Exception.*", line):
                insights += (line) + ", "

            if (line.find('classes/:na')!=-1):
                pattern = r"at ([\w\.]+)\.([\w\$]+)\(([\w\.]+)\.java:(\d+)\)"
                match = re.match(pattern,line)

                if match:
                    class_name, method_name, file_name, line_number = match.groups()
                    #print(f"Class: {class_name}, Method: {method_name}, File: {file_name}, Line: {line_number}")
                    insights += (f"Class: {class_name}, Method: {method_name}, File: {file_name}, Line: {line_number}") + ", "


        return insights
