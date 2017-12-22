
import requests
from datetime import datetime, timedelta, timezone
import calendar
import time
import urllib.request
import json
import csv

CONST_HEADERS = {'Content-type': 'application/json'}
CONST_CSV_HEADINGS = ['User', 'Time Logged', 'Time Logged Sec','Work Log ID', 'Date', 'Timestamp', 'Issue ID','Issue Summary', "Original Estimate",
'Aggregate Time Spent', 'Status', 'Last Run', 'Last Run epoch', '#Dev Review Returns', '#QA Review Returns']
CONST_PATTERN_YMDHMS = '%Y-%m-%dT%H:%M:%S'
CONST_PATTERN_YMDHMS_UTC = "UTC Time: %Y-%m-%d %H:%M:%S+00:00 (UTC)"
CONST_PATTERN_YMDHMS_FILENAME = 'workLog_%Y%m%dT%H%M%S.csv'
domain = "https://%s.atlassian.net"
userid = ""
password = ""

def calcAndPrintDate(timeFrame, unixTimestamp):   
    print(timeFrame)
    print("Epoch as GMT: " + str(unixTimestamp))
    localTime = time.localtime(unixTimestamp)
    utcTime = time.gmtime(unixTimestamp)
    print(time.strftime(CONST_PATTERN_YMDHMS, localTime)) 
    print(time.strftime(CONST_PATTERN_YMDHMS_UTC, utcTime)) 
    return;   

def getWorkLogs(fromDate=0, toDate=0):   
    try:
        if fromDate == 0 and toDate == 0:    
            workLogIDs = requests.get("%s/rest/api/latest/worklog/updated?" %domain,
                auth=requests.auth.HTTPBasicAuth(userid,password), headers=CONST_HEADERS)
            workLogIDsJSON = workLogIDs.json()
            print("\n# of Worklogs since beginning: " + str(len(workLogIDsJSON["values"])))

        if fromDate == 0 and toDate > 0:    
            workLogIDs = requests.get("%s/rest/api/latest/worklog/updated?since=%s000"
                %(domain, fromDate),
                auth=requests.auth.HTTPBasicAuth(userid,password), headers=CONST_HEADERS)
            localTimeStart = time.localtime(fromDate)
            workLogIDsJSON = workLogIDs.json()
            print("\n# of Worklogs since " + time.strftime(CONST_PATTERN_YMDHMS, localTimeStart) + ": " + str(len(workLogIDsJSON["values"])))

        if fromDate > 0 and toDate > 0:    
            workLogIDs = requests.get("%s/rest/api/latest/worklog/updated?since=%s000&since=%s000" 
            %(domain, fromDate, toDate),
            auth=requests.auth.HTTPBasicAuth(userid,password), headers=CONST_HEADERS)
            workLogIDsJSON = workLogIDs.json()
            localTimeStart = time.localtime(fromDate)
            localTimeEnd = time.localtime(toDate)
            print("\n# of Worklogs from " + time.strftime(CONST_PATTERN_YMDHMS, localTimeStart) + " to " +
                time.strftime(CONST_PATTERN_YMDHMS, localTimeEnd) + ": "  +
                str(len(workLogIDsJSON["values"])))
    except Exception as e:
        print ("Error: %s" % str(e))
    print("Worklog Updated Status Code: " + str(workLogIDs.status_code))
    return workLogIDsJSON;

def buildWorkLogIDList(workLogIDsJSON):
    workLogIdsArray = []
    #create an array of the worklog IDs and sort it
    for x in range(0, len(workLogIDsJSON["values"])):
            workLogIdsArray.append(workLogIDsJSON["values"][x-1]["worklogId"])
    workLogIdsArray.sort()

    #build a string of IDs to pass to API        
    workLogIDList = '{"ids": ['
    for x in range(0, len(workLogIdsArray)):
        workLogIDList = workLogIDList + str(workLogIdsArray[x])
        if x !=len(workLogIdsArray)-1:
            workLogIDList = workLogIDList + ','
    workLogIDList = workLogIDList + ']}'

    #DEBUG
    #workLogIDList = '{"ids": [10613, 10614, 10615,10616]}'
    #workLogIDList = '{"ids": [10132]}'
    #print (workLogIDList)
    return workLogIDList;   

def writeHeadings(writer, buffer):
    writeData(writer, buffer)
    return;

def writeData(writer, buffer):
    try:
        writer.writerow(buffer)
    except Exception as e2:
        writer.writerow("***Error Occurred Processing...")
        print ("Error: %s" % str(e2))
    return;

def getWorkLogData(workLogIDs):
    try:
        workLogListData = requests.post("%s/rest/api/latest/worklog/list" %domain, data=workLogIDs,
            auth=(userid,password), headers=CONST_HEADERS)
        print("\nWorklog List Status Code: " + str(workLogListData.status_code))
    except Exception as e2:
        print ("Error: %s" % str(e2))
    return workLogListData;

def getStatusChanges(issueDataJSON):
    #get changes
    failedDevReview = 0
    failedQAReview = 0
    failures = []
    for changelogCount in range(0, issueDataJSON["changelog"]["total"]):
        changeData = issueDataJSON["changelog"]["histories"][changelogCount]
        for changeItemCount in range(0, len(changeData["items"])):
            if (changeData["items"][changeItemCount]["field"] == 'status'):
                changeItem = changeData["items"][changeItemCount]
                if (changeItem["toString"] == "Returned to Development"):
                    if (changeItem["fromString"] == "Development Review"):
                        failedDevReview = failedDevReview + 1
                    else:
                        failedQAReview = failedQAReview + 1
    failures.append(failedDevReview);
    failures.append(failedQAReview);
    return failures;

def buildOutputRow(offset, workLogListDataJSON, issueDataJSON, nowUtcEpoch):
    dateStarted = workLogListDataJSON[offset]["started"]
    strippedSummary =  issueDataJSON["fields"]["summary"].replace(',','')
    author = workLogListDataJSON[offset]["updateAuthor"]["displayName"]
    timeSpent = workLogListDataJSON[offset]["timeSpent"]
    timeSpentSeconds = workLogListDataJSON[offset]["timeSpentSeconds"]
    issueKey = issueDataJSON["key"]
    timeoriginalestimate = issueDataJSON["fields"]["timeoriginalestimate"]
    aggregatetimespent = issueDataJSON["fields"]["aggregatetimespent"]
    status = issueDataJSON["fields"]["status"]["name"]
    localTimeEnd = time.localtime(nowUtcEpoch)
    runTime = time.strftime(CONST_PATTERN_YMDHMS, localTimeEnd)
    runTimeEpoch = str(nowUtcEpoch)
    workLogId = workLogListDataJSON[offset]["id"]
    failuresArray = getStatusChanges(issueDataJSON)
    buffer = [author, timeSpent, timeSpentSeconds, workLogId, dateStarted[0:10], dateStarted,
            issueKey, strippedSummary, timeoriginalestimate, aggregatetimespent, status, runTime, 
            runTimeEpoch, failuresArray[0], failuresArray[1]]
    print (offset, workLogId, dateStarted[0:10], strippedSummary)
    return buffer;

def determineStartEndTimes(lastRunUtcEpoch=0):
    startEndTimes = []
    #now
    nowDate = datetime.now().strftime(CONST_PATTERN_YMDHMS)
    # print("Now ISO: " + datetime.now().isoformat())
    # print("Now UTC ISO as Central: " + datetime.now(timezone.utc).astimezone().isoformat())
    # print("Now UTC ISO: " + datetime.utcnow().isoformat())
    # print("Now UTC ISO as UTC: " + datetime.now(timezone.utc).isoformat())

    #How far back we want to go? use this if we wanted to go back x days from today
    # lastTs = datetime.now() - timedelta(days=1)
    # lastDate = lastTs.strftime(CONST_PATTERN_YMDHMS)
    # print("Last Date HMS: " + str(lastDate))
    # lastTimeTuple = time.strptime(lastDate, CONST_PATTERN_YMDHMS)
    # lastRunUtcEpoch = int(time.mktime(lastTimeTuple))

    #GMT Time as ecpoch
    nowTimeTuple = time.strptime(nowDate, CONST_PATTERN_YMDHMS)
    nowUtcEpoch = int(time.mktime(nowTimeTuple))
    calcAndPrintDate("Now",nowUtcEpoch)
    calcAndPrintDate("Previous Run",lastRunUtcEpoch)
    startEndTimes.append(lastRunUtcEpoch)
    startEndTimes.append(nowUtcEpoch)
    return startEndTimes;

#main routine
#lastRunTSUtcEpoch = 1513285490

userid = input("Please enter JIRA userid:")
password = input("Please enter JIRA password:")
client = input("Please enter JIRA domain:")
domain = (domain %client)

lastRunTSUtcEpoch = input("Please enter last run time (epoch):")
runTimes = determineStartEndTimes(int(lastRunTSUtcEpoch))

continueProcessing = True
#workLogIDsJSON = getWorkLogs() # to run pulling all data
workLogIDsJSON = getWorkLogs(fromDate=runTimes[0], toDate=runTimes[1])
while continueProcessing:
    workLogIDList = buildWorkLogIDList(workLogIDsJSON)
    if len(workLogIDList) > 0:
        workLogListData = getWorkLogData(workLogIDList)
        if workLogListData.status_code == 200:
            workLogListDataJSON = workLogListData.json()
            fileName = datetime.now().strftime(CONST_PATTERN_YMDHMS_FILENAME)
            try:
                with open(fileName, 'a') as outcsv:   
                    #configure writer to write standard csv file
                    writer = csv.writer(outcsv, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                    writeHeadings(writer, CONST_CSV_HEADINGS)
                    for x in range(0, len(workLogListDataJSON)):
                        issueDetail = requests.get("%s/rest/api/2/issue/%s?expand=changelog" %(domain, workLogListDataJSON[x]["issueId"]),
                            auth=requests.auth.HTTPBasicAuth(userid,password), headers=CONST_HEADERS)
                        if issueDetail.status_code == 200:
                            issueDataJSON = issueDetail.json()
                            if ((issueDataJSON["fields"]["project"]["key"] == "BFD") or 
                                (issueDataJSON["fields"]["project"]["key"] == "WD" and workLogListDataJSON[x]["updateAuthor"]["displayName"] == "Ang Li")):
                                writeData(writer, buildOutputRow(x, workLogListDataJSON, issueDataJSON, runTimes[1]))
                            else:
                                print (x, workLogListDataJSON[x]["id"], "* Different Project: ", issueDataJSON["fields"]["project"]["key"])
                        else:
                            print("No access to project!")
                    else:
                        if workLogIDsJSON["lastPage"] == False:
                            #do another read
                            nextCall = workLogIDsJSON["nextPage"]
                            #nextCall = "http://www.example.com/jira/worklog/updated/updated?since=1438013671136&since=1438013693137"
                            startPos1 =  nextCall.find("?since=")
                            startPos2 = nextCall.find("&since=")
                            if startPos2 > 0:
                                nextFrom = nextCall[startPos1+7:startPos2]
                                nextTo = nextCall[startPos2+7:len(nextCall)-3]
                            else:
                                nextFrom = nextCall[int(startPos1+7):len(nextCall)-3]
                            runTimes = determineStartEndTimes(int(nextFrom))
                            workLogIDsJSON = getWorkLogs(fromDate=runTimes[0], toDate=runTimes[1])
                        else:
                            continueProcessing = False
            except Exception as e:
                print ("Error: %s" % str(e))
        else:
            print("\nNo workLogListData Records Found!")
    else:
        print("\nNo workLogIDs Records Found!")
print("Done Processing")
