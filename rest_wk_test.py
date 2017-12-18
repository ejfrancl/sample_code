import requests
from datetime import datetime, timedelta, timezone
import calendar
import time
import urllib.request
import json
import csv
import base64

CONST_URL = ""
CONST_ID = "eddie.francl@centricconsulting.com"
CONST_PWD = ""
CONST_PWD2 = ""
CONST_SUCCESS = "SUCCESS"
CONST_PATTERN_YMDHMS = '%Y-%m-%dT%H:%M:%S'
CONST_PATTERN_YMDHMS_RESUME_FILENAME = 'resume_%Y%m%dT%H%M%S.txt'
CONST_PATTERN_YMDHMS_COVER_FILENAME = 'cover_%Y%m%dT%H%M%S.txt'
CONST_PATTERN_YMDHMS_TODO_FILENAME = 'todo_%Y%m%dT%H%M%S.txt'
sessionID = ""
sessionToken = ""

CONST_HEADERS = {
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
}

def issueCall(call, args):
    callBody = 'function=%s'%(call)
    for x in range(0, len(args)):
        callBody = callBody + "&%s"%(args[x])
    try:
        response = requests.post(CONST_URL, data=callBody, headers=CONST_HEADERS)
        print("\n%s: "%(call) + str(response.status_code) + " - " + response.text)
        resultJSON = json.loads(response.text)
        status = resultJSON["result"]["status"]
        message = resultJSON["result"]["message"]
        data = resultJSON["result"]["data"]
    except Exception as e2:
        print ("Error: %s" % str(e2))%s
    return resultJSON["result"];

def createID(args):
    result = issueCall("post_new_user", args)
    print(result["status"] + " : " + result["message"])
    return result;

def login(id, pwd, createID=False):
    args = []
    global sessionID
    global sessionToken
    
    args.append("user="+id)
    args.append("password="+pwd)
    if createID:
        createID(args)
    result = issueCall("login", args)
    if result["status"] == CONST_SUCCESS:
        localTime = time.localtime(int(result["data"]["expires"]))
        print("Session Expire: " + time.strftime(CONST_PATTERN_YMDHMS, localTime))
        sessionID = result["data"]["session"]
        sessionToken = result["data"]["token"]
    else:
        print(result["status"] + " : " + result["message"])
    return result;

def createFile(fileName):
    try:
        with open(fileName, 'rb') as f:
            file_read = f.read()
            f_64_encode = base64.encodestring(file_read)
            # print(file_read)
            # print(f_64_encode)
            # f_64_decode = base64.decodestring(f_64_encode) 
            # f_result = open('test_decode.txt', 'wb') # create a writable and write the decoding result
            # f_result.write(f_64_decode)
    except Exception as e2:
        print ("Error: %s" % str(e2))%s
    return f_64_encode;

def renew(call, args):
    global sessionID
    global sessionToken
    result = issueCall(call, args)
    if result["status"] == CONST_SUCCESS:
        sessionID = result["data"]["session"]
        sessionToken = result["data"]["token"]
        localTime = time.localtime(int(result["data"]["expires"]))
        print("Session Expire: " + time.strftime(CONST_PATTERN_YMDHMS, localTime))
    else:
        print(result["status"] + " : " + result["message"])
    return result;

def password(args):
    result = issueCall("post_forgot_password", args)
    code = ""
    print(result["status"] + " : " + result["message"])
    if result["status"] == CONST_SUCCESS:
        args.clear()
        args.append("user="+CONST_ID)
        code = input("What is the reset code?")
        args.append("code="+code)
        result = issueCall("post_verify_code", args)
        print(result["status"] + " : " + result["message"])
    if result["status"] == CONST_SUCCESS:
            args.clear()
            args.append("user="+CONST_ID)
            args.append("code="+code)
            args.append("password="+CONST_PWD2)
            result = issueCall("post_reset_password", args)
            print(result["status"] + " : " + result["message"])
    return;

def setUserData(call, args):
    args.clear()
    args.append("session="+sessionID)
    args.append("token="+sessionToken)

    userData = {
        "Prefix":"Mr.",
        "Suffix":"Jr.",
        "FirstName":"Eddie",
        "Initials":"J.",
        "LastName":"Francl",
        "PreferredEmail":"eddie.francl@centricconsulting.com",
        "AltEmail":"eddie.francl@centricconsulting.com",
        "PreferredPhone":{  
            "Number":"123-555-1234",
            "Type":"Work"
        },
        "AltPhone":{  
            "Number":"123-555-5678",
            "Type":"Mobile"
        },
        "Employment":{  
            "JobTitle":"Senior Manager",
            "Company":"Testing Inc.",
            "City":"Chicago",
            "State":"IL",
            "StartDate":"2017-01-22"
        },
        "ResumeName":"The_Resume.doc",
            "ResumeDate":"2017-10-22"
        }
    args.append("data="+json.dumps(userData,default=str))
    result = issueCall("post_user_data", args)
    print(result["status"] + " : " + result["message"])
    return result;

def setUserSettings(call, args):
    args.clear()
    args.append("session="+sessionID)
    args.append("token="+sessionToken)
    userData = {
        "PositionTypes":{  
            "Industry":[  
                1023,
                1024
            ],
            "Category":[  
                10,
                11,
                12
            ]
        },
        "RegionPrefs":{  
            "Region":[  
                1,
                2
            ],
            "State":[  
                4510
            ],
            "Locale":[  
                1,
                2
            ],
            "City":[  
                4638,
                4604
            ]
        },
        "EmailPrefs":{  
            "RecruitConsent":"false",
            "MarketingConsent":"true",
            "AreaInterestConsent":"false"
        }
    }

    args.append("data="+json.dumps(userData,default=str))
    result = issueCall("post_user_settings", args)
    print(result["status"] + " : " + result["message"])
    return result;

def getGeneric(call, args):
    result = issueCall(call, args)
    if result["status"] == CONST_SUCCESS:
        print("%s : "%call + str(result["data"]))
    else:
        print(result["status"] + " : " + result["message"])
    return result; 

def getPositions(call, args):
    parms = {  
        "keywords":"senior manager",
        "category":103,
        "location":4405,
        "practice":751
    }

    if len(parms) > 0:
        args.append("params="+json.dumps(parms))
    result = getGeneric(call, args)
    return result; 

def setSession(args):
    args.append("session="+sessionID)
    args.append("token="+sessionToken)
    return args;

#main routine
#test = input("Press any key to start....")
result = login(CONST_ID, CONST_PWD2)

args = []
setSession(args)
result = renew("renew_login", args)

args.clear()
setSession(args)
result = getGeneric("get_lookups", args)

args.clear()
args.append("user="+CONST_ID)
#password(args)

args.clear()
setSession(args)
userData = getGeneric("get_user_data", args)
userData = setUserData("post_user_data", args)

args.clear()
setSession(args)
#TODO
args.append("type="+"resume") #cover #todo
args.append("parse="+"false") #true - only valid for resume
resumeFileName = datetime.now().strftime(CONST_PATTERN_YMDHMS_RESUME_FILENAME)
coverFileName = datetime.now().strftime(CONST_PATTERN_YMDHMS_COVER_FILENAME)
todoFileName = datetime.now().strftime(CONST_PATTERN_YMDHMS_TODO_FILENAME)
fileName = 'test.txt'
args.append("doc_base64="+ str(createFile(fileName)))
result = getGeneric("post_document", args)

args.clear()
setSession(args)
result = getGeneric("get_user_settings", args)
result = setUserSettings("post_user_settings", args)

args.clear()
setSession(args)
result = getGeneric("get_active_jobs", args)
result = getGeneric("get_past_jobs", args)

args.clear()
setSession(args)
result = getPositions("get_positions", args)

args.clear()
setSession(args)
jobID = "494"
args.append("id="+jobID)
result = getGeneric("get_job_details", args)

args.clear()
setSession(args)
referralString = "blah blah"
args.append("referral="+referralString)
jobID = "494"
args.append("id="+jobID)
#TODO
useCurrentResume = "False" #true
args.append("use_onfile_resume="+useCurrentResume)
resumeFileName = datetime.now().strftime(CONST_PATTERN_YMDHMS_RESUME_FILENAME)
coverFileName = datetime.now().strftime(CONST_PATTERN_YMDHMS_COVER_FILENAME)
fileName = 'test.txt'
args.append("resume_base64="+ str(createFile(fileName))) #optional
args.append("cover_base64="+ str(createFile(fileName))) #optional
result = getGeneric("post_apply", args)

args.clear()
setSession(args)
referralString = "blah blah"
args.append("referral="+referralString)
jobID = "494"
args.append("id="+jobID)
nomination = {  
   "Prefix":"Mr.",
   "Suffix":"Jr.",
   "FirstName":"Thomas",
   "Initials":"H.",
   "LastName":"Choate",
   "PreferredEmail":"tchoate@somethere.com",
   "PreferredPhone":"123-555-1234",
   "Employment":{  
      "JobTitle":"Senior Manager",
      "Company":"Testing Inc."
   },
   "Comments":"A detailed write-up of why Thomas would be a good fit for the job."
}
args.append("data="+json.dumps(nomination))
#TODO
args.append("anonymous="+"false") #true
result = getGeneric("nomination", args)

print("Done Processing")
