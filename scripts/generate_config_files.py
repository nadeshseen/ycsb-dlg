import os
import subprocess
import json

# https://stackoverflow.com/questions/845058/how-to-get-line-count-of-a-large-file-cheaply-in-python
def file_len(fname):
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])

def split_files(config_filename):
    json_data_file =  open(config_filename)
    data = json.load(json_data_file)
    file_name = data["trace_file_name"]
    
    trace_splits_path = data["trace_splits_path"]

    workload_template = data["workload_template"]

    n_splits = 0
    active_file_name=""
    for machines in data["machines"]:

        if machines["status"]=="active":
            if machines["send_trace_file"]=="true":
                n_splits+=1
                active_file_name=machines["name"]


    parameter_count=0
    if n_splits==0:
        for machines in data["machines"]:
            if machines["status"]=="active":
                if machines["send_trace_file"]=="false":
                    parameter_count+=1
                    
                    data = open(workload_template)
                    data = data.read()
                    # print(data)
                    data = data.replace("<core_path>", machines["workload_parameter"]["core_path"])
                    data = data.replace("<recordcount>", machines["workload_parameter"]["recordcount"])
                    data = data.replace("<operationcount>", machines["workload_parameter"]["operationcount"])
                    data = data.replace("<readproportion>", machines["workload_parameter"]["readproportion"])
                    data = data.replace("<updateproportion>", machines["workload_parameter"]["updateproportion"])
                    data = data.replace("<insertproportion>", machines["workload_parameter"]["insertproportion"])
                    data = data.replace("<requestdistribution>", machines["workload_parameter"]["requestdistribution"])
                    # print(data)
                    path="./workloads/"
                    new_file_name="parameter_"+machines["name"]
                    
                    # print file name
                    # print(new_file_name)

                    new_file = open(path+new_file_name, "w")
                    new_file.write(data)
    elif n_splits==1:
        path = trace_splits_path
        new_file_name = "kv_trace_"+active_file_name+".dat"
        os.system("cp "+ file_name +" "+path+ new_file_name)
        print(machines["name"],new_file_name, file_len(path+new_file_name))
    else:
        split_ratio = []
        for machines in data["machines"]:
            if machines["status"]=="active":
                if machines["send_trace_file"]=="true":
                    split_ratio.append(machines["trace_percentage"])

        
        n_lines = file_len(file_name)
        print(n_lines)
        ratio_sum = 0
        for i in range(n_splits):
            ratio_sum += int(split_ratio[i])

        # print(ratio_sum)

        split_line_no = []
        for i in range(n_splits):
            # print("Number of lines in File "+str(i+1)+" : "+str(int(int(split_ratio[i])*n_lines/ratio_sum)))
            if i==0:
                split_line_no.append(int(int(split_ratio[i])*n_lines/ratio_sum))
            elif i!=n_splits-1:
                split_line_no.append(split_line_no[i-1] + int(int(split_ratio[i])*n_lines/ratio_sum))

        # print(split_line_no)
        str_split_line_no = ""
        for i in split_line_no:
            str_split_line_no += str(i+1) + " "
        # print(str_split_line_no)

        # print()
        # os.system("bash testing.sh "+str_split_ratio)
        comm = "cd splitted_files && csplit -s "+file_name+" --prefix='kv_trace_' --suffix-format='%01d.dat' "+str_split_line_no
        # print(comm)

        os.system(comm)
        i=0
        parameter_count=0
        for machines in data["machines"]:
            if machines["status"]=="active":
                if machines["send_trace_file"]=="true":
                    path = trace_splits_path
                    old_file_name = "kv_trace_"+str(i)+".dat"
                    new_file_name = "kv_trace_"+machines["name"]+".dat"
                    os.rename(path+old_file_name, path+new_file_name)
                    print(machines["name"], file_len(path+new_file_name))
                    i+=1
                else:
                    parameter_count+=1
                    data = open(workload_template)
                    data = data.read()
                    # print(data)
                    data = data.replace("<recordcount>", machines["workload_parameter"]["recordcount"])
                    data = data.replace("<core_path>", machines["workload_parameter"]["core_path"])
                    data = data.replace("<operationcount>", machines["workload_parameter"]["operationcount"])
                    data = data.replace("<readproportion>", machines["workload_parameter"]["readproportion"])
                    data = data.replace("<updateproportion>", machines["workload_parameter"]["updateproportion"])
                    data = data.replace("<insertproportion>", machines["workload_parameter"]["insertproportion"])
                    data = data.replace("<requestdistribution>", machines["workload_parameter"]["requestdistribution"])
                    # print(data)
                    path="./workloads/"
                    new_file_name="parameter_"+machines["name"]
                    
                    # print file name
                    # print(new_file_name)

                    new_file = open(path+new_file_name, "w")
                    new_file.write(data)
    print("Worker nodes with trace input =",str(n_splits))
    print("Worker nodes with non-trace input =",parameter_count)
    

if __name__=="__main__":
    split_files()