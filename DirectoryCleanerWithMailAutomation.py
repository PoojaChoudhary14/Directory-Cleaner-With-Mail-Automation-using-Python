from sys import *
import os
import hashlib
import time
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import password
import schedule


####################################################################################
def mailFile(attachPath,fileName,receiverID):
    email_sender=password.mailID
    email_password=password.pwd
    email_receiver=receiverID

    subject='Log File of all deleted Files'
    body="""
   Please find the attached copy of log file created.
    """
    attachment_Name=attachPath
    attachment_File=open(attachment_Name,'rb')
    em=MIMEMultipart()
    em['From']=email_sender
    em['To']=email_receiver
    em['Subject']=subject
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload(attachment_File.read())
    encoders.encode_base64(payload)
    name=fileName+'.txt'
    payload.add_header('Content-Disposition', "attachement; filename=%s"%name)
    em.attach(MIMEText(body)) #to attach body in mail
    em.attach(payload)        #to attach payload in mail

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com',465,context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver,em.as_string())


###############################################################################

def DeleteFiles(dict1):
    results=list(filter(lambda x: len(x)>1 , dict1.values()))
    icnt=0

    if len(results)>0:
        for result in results:
            for subresult in result:
                icnt+=1
                if icnt>=2:
                    os.remove(subresult)
            icnt=0

    

##############################################################################




def hashfile(path,blocksize=1024):
    afile=open(path,'rb')
    hasher=hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf)>0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()

#############################################################################


def FindDup(path):
    flag=os.path.isabs(path)
    
    if flag == False:
        path = os.path.abspath(path)

    exists = os.path.isdir(path)

    dups={}
    if exists:
        for dirName,subdirs,fileList in os.walk(path):
            
            for filen in fileList:
                
                path=os.path.join(dirName,filen)
                file_hash = hashfile(path)

                if file_hash in dups:
                    dups[file_hash].append(path)
                else:
                    dups[file_hash]=[path]

        return dups

    else:
        print("Invalid Path")

#####################################################################################


def PrintDuplicateintoFile(dict1,log_dir="Marvellous"):
    results = list(filter(lambda x :len(x)>1 ,dict1.values()))

    if not os.path.exists(log_dir):
        try:
            os.mkdir(log_dir)
        except:
            pass

    
    separator="-"*80
    fileName="MarvellousLog%s.log"%(time.ctime())
    log_path=os.path.join(log_dir,"MarvellousLog%s.log"%(time.ctime()))
    log_path=log_path.replace(" ","")
    log_path=log_path.replace(":","")
    f=open(log_path,'w')
    f.write(separator+"\n")
    f.write("Duplicate Files Removed:"+time.ctime()+"\n")
    f.write(separator+"\n")

    if(len(results)>0):
        f.write("Duplicate found:")

        f.write("The following are identitical.")

        icnt=0
        for result in results:
            for subresult in result:
                
                icnt+=1
                if icnt>=2:
                    f.write('%s'%subresult)
                    f.write("\n")
            icnt=0

    else:
        f.write("No duplicate found.")

    return log_path,fileName

#####################################################################################################


def TaskScheduled():
    try:
        arr ={}
        startTime=time.time()
        arr=FindDup(argv[1])
        FilePath,FileName=PrintDuplicateintoFile(arr)
        DeleteFiles(arr)
        mailFile(FilePath,FileName,argv[3])
        

        

    except ValueError:
        print("Error : Invalid datatype of input")
    
    except Exception as E:
        print("Error : Invalid input",E)
                
######################################################################################################
    
def main():
    
    print("Application name :"+argv[0])

    if(len(argv)!=4):
        print("Error : Invalid number of arguments")
        exit()
    
    if(argv[1] == '-h' or argv[1]=='-H'):
        print("This script is used to traverse specific directory, delete duplicate files and save the details of all duplicate files into a directory ")
        exit()
    
    if(argv[1]=='-U' or argv[1]=='-u'):
        print("Usage : ApplicationName  AbsolutePath_of_Directory TimeInterval Receiver mail id")
        exit()

    schedule.every(argv[2]).minutes.do(TaskScheduled)

    while(True):
        schedule.run_pending()
        time.sleep(1) #to reduce load on CPU

    

if __name__=="__main__":
    main()
