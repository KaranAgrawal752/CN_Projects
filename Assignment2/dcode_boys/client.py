import socket
import threading

# Server information
SERVER_HOST = "10.17.7.134"
SERVER_PORT = 9801  

# Master information
MASTER_HOST="10.194.58.44"
MASTER_PORT=12345
file_input=""
# Flag  
flag_master=[0]*1000
flag_server=[0]*1000
messages=['']*1000
cnt_master=0
cnt_server=0
queue=[]
stop_master=0
final_stop=0

def connect_server(thread_run, server_host,server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print(f'[{SERVER_HOST}] connecting')
    client_socket.connect((server_host, server_port))
    client_socket.sendall("SESSION RESET\n".encode())
    data_recv=client_socket.recv(32).decode('utf-8')
    # print(f'Session Reset {data_recv}')
    # print(f'[{SERVER_HOST}] connected')
    message = "SENDLINE\n"
    global file_input
    global cnt_server
    global cnt_master
    global stop_master
    global final_stop

    while cnt_server!=1000 and stop_master==0:
        # print('sending message to server')
        client_socket.sendall(message.encode())
        response=""
        line_count=0

        while line_count<2:
            data = client_socket.recv(1024).decode('utf-8')
            response+=data
            line_count +=data.count('\n') 
              
        if(response[0:2]=="-1"):
            continue

        # print("Server response:", response)
        rp=response.split("\n")
        line,message1=rp[0],rp[1]
        line=int(line)
        # print(line)

        if flag_server[line]==0:
            flag_server[line]=1
            # messages_lock.acquire()
            messages[int(line)]=message1+"\n"
            # messages_lock.release()
            cnt_server +=1

            if flag_master[line]==0:
                flag_master[line]=1
                # cnt_master_lock.acquire()
                cnt_master+=1
                # cnt_master_lock.release()
                # queue_lock.acquire()
                queue.append(line)
                # print(line)
                # print(queue[-1])
                # queue_lock.release()

    # print(queue)
    # print(len(queue))
    while final_stop==0:
        continue
    send_file = "SUBMIT\n" + "mcs232487@dcode_boys\n" + "1000\n" + file_input
    try:
        client_socket.sendall(send_file.encode())
    except Exception as e:
        print("[ERROR] File sending error : [%s]" % str(e))

    try:
        submission_data = ""
        lcount = 0
                
        while lcount != 1:
            sdata = client_socket.recv(1024)
            submission_data += sdata.decode('utf-8')
            lcount = submission_data.count('\n')

        sline = submission_data.split('\n')
        # print(sline[0])

    except Exception as e:
        print("Error in submission")
    try:
        sline_list=submission_data.split("-")[3].split(", ")
        total_time = int(sline_list[2]) - int(sline_list[0])
        print(f'Total time taken is {total_time} ms')
    
    except Exception as e:
        print("Error in time printing")
    
    client_socket.close()
    # print(messages)
    # print(cnt_server)

def connect_master(thread_run, master_host,master_port):
    global file_input
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print(f'[{master_host}] connecting')
    client_socket.connect((master_host, master_port))
    print(f'[{master_host}] connected')
    message=""
    while True:
        previous_line=-1
        while True:

            # queue_lock.acquire()
            if len(queue)==0:
                # queue_lock.release()
                break
            current_line=queue.pop(0)
            # queue_lock.release()
            if message=="":
                message = client_socket.recv(128).decode('utf-8')
                # print(f'The message recieved from Master {message} A')
            if message=="STOP\n":
                print("STOPPED\n")
                break
            if message=="SENDMESSAGE\n":
                # messages_lock.acquire()
                client_socket.sendall(messages[previous_line].encode())
                # messages_lock.release()
                message=""
                if message=="":
                    message=client_socket.recv(128).decode('utf-8')
                    # print(f'The message recieved from Master {message} B')
                if message=="STOP\n":
                    print("STOPPED\n")
                    break
            client_socket.sendall((str(current_line)+"\n").encode())
            message=""
            previous_line=current_line
        if previous_line!=-1 and message!="STOP\n":
            if message=="":
                message = client_socket.recv(128).decode('utf-8')
                # print(f'The message recieved from Master {message} C')
            if message=="SENDMESSAGE\n":
                # messages_lock.acquire()
                # print(previous_line, messages[previous_line])
                client_socket.sendall(messages[previous_line].encode())
                # print("C")
                # messages_lock.release()
                message=""
                if message=="":
                    message=client_socket.recv(128).decode('utf-8')
                    # print(f'The message recieved from Master {message} B')
            if message=='STOP\n':
                print("STOPPED\n")
                break
        # cnt_master_lock.acquire()
        if cnt_master>=1000 or message=="STOP\n":
            # cnt_master_lock.release()
            break
        # cnt_master_lock.release()
    global stop_master
    global final_stop
    global file_input
    lcount = 0
    stop_master=1
    while lcount != 2000:
        message_recv = client_socket.recv(1024).decode('utf-8')
        file_input += message_recv
        lcount += message_recv.count('\n')
    
    final_stop=1
    client_socket.close()



def main():
    thread_run = True
    t1 = threading.Thread(target=connect_server, args=(lambda: thread_run, SERVER_HOST, SERVER_PORT))
    t1.start()
    t2 = threading.Thread(target=connect_master, args=(lambda: thread_run, MASTER_HOST, MASTER_PORT))
    t2.start()
    t2.join()
    t1.join()

if __name__=='__main__':
    main()

