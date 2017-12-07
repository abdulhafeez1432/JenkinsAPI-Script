import requests #Modules used for the url
import jenkins #Jenkins Modules for the API
from sqlalchemy import * #ORM Databse for SQLITE 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime #Date and Time Modules
import sys #Is used to terminate the Error, if the Username and PAssword is not correct.

Base = declarative_base()

#Jenkins Connection Details for the API
def connectToJenkins(url, username, password):
    
    server = jenkins.Jenkins(url, 
    username=username, password=password)
    return server

def initializeDb():
    #Unix/Mac - 4 initial slashes in total
    #engine = create_engine('sqlite:////absolute/path/to/jenkins.db')
    #Windows
    #The Database path should be the path where you create your database to. You can Change the path. And, remeber to use \\ not single
    engine = create_engine('sqlite:///C:\\Users\\Labeeb\\Desktop\\virtualenv\\seedstars\\jenkins_job.db', echo=False)    
    session = sessionmaker(bind=engine)()
    Base.metadata.create_all(engine)
    return session

def addJob(session, jlist):
    for j in jlist:
        session.add(j)
    session.commit()

def getLastJobId(session, name):
    job = session.query(Jobs).filter_by(name=name).order_by(Jobs.jen_id.desc()).first()
    if (job != None):
        return job.jen_id
    else:
        return None
#Classs used to Create the Database for the SQLITE
class Jobs(Base):
    __tablename__ = 'Jobs'

    id = Column(Integer, primary_key = True)
    jen_id = Column(Integer)
    name = Column(String)
    timeStamp = Column(DateTime)
    result = Column(String)
    building = Column(String)
    estimatedDuration = Column(String)

def createJobList(start, lastBuildNumber, jobName):
    jList = []
    for i in range(start + 1, lastBuildNumber + 1):
        current = server.get_build_info(jobName, i)
        current_as_jobs = Jobs()
        current_as_jobs.jen_id = current['id']
        current_as_jobs.building = current['building']
        current_as_jobs.estimatedDuration = current['estimatedDuration']
        current_as_jobs.name = jobName
        current_as_jobs.result = current['result']
        current_as_jobs.timeStamp = datetime.datetime.fromtimestamp(long(current['timestamp'])*0.001)
        jList.append(current_as_jobs)
    return jList



while True:
    url = 'http://localhost:8080' #The default Host for Jenkins
    username = input('Enter username: ') #Python Input function to Enter your Username
    password = input('Enter password: ') #Python Input function to Enter your Password
    server = connectToJenkins(url, username, password)
    authenticated = false
    try:
        server.get_whoami()
        authenticated = true
    except jenkins.JenkinsException as e:
        print('Username or Password is not Correct, Please, Enter Correct USername and Password')
        authenticated = false
        sys.exit(1) #This terminate the program if the Username and password is not correct
    confirm == False
else:
    if authenticated:
        session = initializeDb()

        # get a list of all jobs
        jobs = server.get_all_jobs()
        for j in jobs:
            jobName = j['name'] # get job name
            #print jobName
            lastJobId = getLastJobId(session, jobName) # get last locally stored job of this name
            lastBuildNumber = server.get_job_info(jobName)['lastBuild']['number']  # get last build number from Jenkins for this job 
            
            # if job not stored, update the db with all entries
            if lastJobId == None:
                start = 0
            # if job exists, update the db with new entrie
            else:
                start = lastJobId

            # create a list of unadded job objects
            jlist = createJobList(start, lastBuildNumber, jobName)
            # add job to db
            addJob(session, jlist)
        print("The Job Data has been Successful Stored in the Database")
