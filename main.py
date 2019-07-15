import pymongo, flask, datetime, xmltodict, json
# import pprint
from datetime import timedelta, datetime
from flask import Flask, request, render_template, url_for, redirect
from bson.objectid import ObjectId

import xyleme_helper
from xyleme_helper import *


app = Flask(__name__)


# making a connection to the db
myclient = pymongo.MongoClient("mongodb://localhost:27017/")  # connection url
mydb = myclient['scheduledb'] # connection to db
mycol = mydb['modules'] # choosing a collection

# setting defaults
defaultDuration = 5
startTime = '09:00'
endTime ='17:00'
lunchTime = '12:00'
lunchduration = 45


# HOMEPAGE
@app.route("/", methods=["GET", "POST"])
def root():
    errors = []  # creating an empty lis tto store error messages
    if request.method == 'POST':  # checking what type of request it is
        guid = request.form.get('guid')  # getting the guid from the user's input
        
        module = getModule(guid)  # getting a module using the guid (as xml)
        if module is None:  # if None is returned then no course has that guid
            errors.append('This course does not exist')  # appending an error message to the list
            data = mycol.find({})  # getting all the data from the db
            
            return render_template('home.html', modules=data, errors=errors)
        
        createDict(module)  # converting to dictionary
        
        return redirect(url_for('root'))
        
    else:
        data = mycol.find({})  # getting all the data from the db

        return render_template('home.html', modules=data, errors=errors)


# SCHEDULE PAGE
@app.route("/topics/<id>", methods=["GET", "POST"])
def topics(id):
    errors = []     # creating an empty list for the errors
    
    # variables for form values
    form1Values = None
    form2Values = None
    
    if request.method == 'POST':  # checking if it is a POST request
        if 'form1' in request.form:
            errors, form1Values = processform1(id, request)   # if it is then process the values entered by the user to check if there are any errors
        else:
            errors, form2Values = processform2(id)

    # checking if the schedule field exists for the chosen module
    count = mycol.count_documents({'_id': ObjectId(id), 'durations': {'$exists': True}}, limit=1)
    if count == 0:  # if it doesn't exist then the defaults are set in the db
        if form1Values is not None and len(errors) > 0:  # checking if errors were found when form1 was processed
            
            return render_template('schedule.html', data=form1Values, id=id, errors=errors)  # return the form values as data if there are errors
            
        # otherwise there are no errors
        mycol.update_one({'_id': ObjectId(id)}, {'$set': {'defaultDuration': defaultDuration, 'startTime': startTime, 'endTime': endTime, 'lunchTime': lunchTime,
                                                      'lunchDuration': lunchduration}})  # update the db with the defaut values
        
        data = mycol.find_one({'_id': ObjectId(id)})  # getting the whole document from the db
    
        return render_template('schedule.html', data=data, id=id, errors=errors)
    
    else:   # otherwise a schedule is generated
        data = mycol.find_one({'_id': ObjectId(id)})  # getting the whole document from the db
        if form2Values is not None and len(errors) > 0:  # checking if errors were found when form2 was processed
            # data["schedule"] = durations
            schedule = newSchedule(form2Values, id)  # create a new schedule using the bad values
        else:
            if form1Values is not None and len(errors) > 0:  # otherwise we check if errors were found when form1 was processed
                data['lunchDuration'] = form1Values['lunchDuration']  # swapping the value taken from the db with the bad value
                
            schedule = newSchedule(data['durations'], id)  # creating a new schedule using the data
            
        return render_template('schedule.html', data=data, schedule=schedule, id=id, errors=errors)


def getForm1(request):  # getting values from form1 as a dictionary
    form1 = {
        'startTime': request.form.get('starttime'),
        'endTime': request.form.get('endtime'),
        'lunchTime': request.form.get('lunchtime'),
        'defaultDuration': int(request.form.get('defduration')),
        'lunchDuration': int(request.form.get('lunchduration'))
    }
    
    return form1


def processform1(id, request):  # processing form1
    errors = []  # creating an empty list for the errors
    
    form1 = getForm1(request)  # getting values from the form
    maxDuration = calcMaxDuration(form1['startTime'], form1['endTime'])  # calculating the max duration for a topic

    if form1['lunchDuration'] not in range(0, maxDuration):  # checking if the lunch duration is between 0 and the max duration
        # if it is not then an error message is appended to the list
        errors.append('The duration of a lunch has to be between 0 and ' + str(maxDuration) + ' minutes (' + str(maxDuration / 60) + ' hours)')
    if form1['defaultDuration'] not in range(0, maxDuration):  # checking if the default duration is between 0 and the max duration
        # if it is not then an error message is appended to the list
        errors.append('The default duration for topics has to be between 0 and ' + str(maxDuration) + ' minutes (' + str(maxDuration / 60) + ' hours)')
        
    if len(errors) > 0:  # checking if there are any errors in the list
        print(len(errors))  # if there are errors then no updates will be done and the messages will be printed on the page
    else:
        if form1['defaultDuration'] == 0:  # this means that a schedule already exists
            updatedb(form1['startTime'], form1['endTime'], form1['lunchTime'], form1['lunchDuration'], id)  # updating the db with the new values
        else:  # otherwise we create a brand new schedule
            durations  = []
            numTopics = countTopics(id)  # counting the number of topics that will have a duration
            
            for i in range(numTopics):
                durations.append(form1['defaultDuration'])
            
            addscheduledb(durations, form1['defaultDuration'], form1['startTime'], form1['endTime'], form1['lunchTime'], form1['lunchDuration'], id)  # updating the db
            
    return errors, form1

            
def processform2(id):  # processing form2
    errors = []  # creating an empty list for the errors
    data = mycol.find_one({'_id': ObjectId(id)})
    # start = data['startTime']
    # end = data['endTime']
    
    maxDuration = calcMaxDuration(data['startTime'], data['endTime'])  # calculating the max duration
    
    inputs = request.form.getlist('input')  # getting the values from the form
    
    for index, i in enumerate(inputs):  # looping through the inputs
        inputs[index] = int(i)  # converting the inputs to integers
        if inputs[index] not in range(0, maxDuration):  # checking if each input is between 0 and the max duration
            errors.append('The duration of a topic has to be between 0 and ' + str(maxDuration) + ' minutes (' + str(maxDuration / 60) + ' hours)')  # append an error message
    if len(errors) > 0:  # checking if there are any errors
        print(len(errors))  # no updates will be done to the db if there errors
    else:
        updatedbschedule(inputs, id)  # updating the db
        
    return errors, inputs


def countTopics(id):  # counting the number of topics in a module
    data = mycol.find_one({'_id': ObjectId(id)}, {'_id': 0, 'course': 1})
    count = 0
    
    #  looping through all the topics in a module and incrementing the counter
    for course in data['course']:
        for lesson in course['lessons']:
            for topic in lesson['topics']:
                count += 1
                    
    return count


def addscheduledb(topicDurationList, defaultDuration, startTime, endTime, lunchTime, lunchDuration, id):  # to set the defaults for a new module
    mycol.update_one({'_id': ObjectId(id)}, {'$set': {'durations': topicDurationList, 'defaultDuration': defaultDuration, 'startTime': startTime, 'endTime': endTime,
                                                  'lunchTime': lunchTime, 'lunchDuration': lunchDuration}})
        
        
def updatedb(startTime, endTime, lunchTime, lunchDuration, id):  # to update the defaults of a module
    mycol.update_one({'_id': ObjectId(id)}, {'$set': {'startTime': startTime, 'endTime': endTime, 'lunchTime': lunchTime, 'lunchDuration': lunchDuration}})
    

def updatedbschedule(durationList, id):  # to update the durations of each topic of a module
    mycol.update_one({'_id': ObjectId(id)}, {'$set': {'durations': durationList}})


def addCourse(name, course):  # adding a course
    mycol.insert_one({'name': name, 'course': course})


def newSchedule(durationList, id):  # making a new schedule for a module
    data = mycol.find_one({'_id': ObjectId(id)})  # getting the current schedule of the chosen module
    sTime = data['startTime']  # getting the start time from the current schedule
    endTime = convertToTime(data['endTime'])  # getting the end time from the current schedule and converting it to a timedelta
    lunchTime = convertToTime(data['lunchTime'])  # getting the lunch time and converting it to a timedelta
    lunchDuration = data['lunchDuration']  # getting the lunch time and its duration from the current schedule
    
    scheduleList = createSchedule(durationList, sTime, endTime, lunchTime, lunchDuration)  # creating a new schedule with the values above

    return scheduleList
    
    
def createSchedule(topicDurationList, sTime, endTime, lunchTime, lunchDuration):  # creating a new schedule
    scheduleList = []  # creating an empty list
    time = datetime.strptime(sTime, '%H:%M')  # setting the time to the start time
    
    for duration in topicDurationList:  # looping through all the durations
        if str(lunchTime + timedelta(minutes=lunchDuration)) > time.strftime('%H:%M:%S') >= str(lunchTime):  # checking if it is lunch time
            start = str(time.strftime('%H:%M'))  # format time to hours and minutes and change type to string
            time = time + timedelta(minutes=lunchDuration)  # adding the lunch duration to the time
            end = str(time.strftime('%H:%M'))  # format time to hours and minutes and change type to string
            
            schedule = {'name': 'LUNCH', 'duration': lunchDuration, 'start': start, 'end': end}  # creating a new dictionary for lunch
            
            scheduleList.append(schedule)  # adding the the dictionary to the list
        
        if str(calcEnd(time, timedelta(minutes=duration)).strftime('%H:%M:%S')) > str(endTime):  # checking if it is the end of the day
            time = datetime.strptime(sTime, '%H:%M')  # if it is then start a new day by setting the time back to the start time
        
        start = str(time.strftime('%H:%M'))  # format time to hours and minutes and change type to string
        time = calcEnd(time, timedelta(minutes=duration))  # getting the time at which the lesson will be over depending on the duration
        end = str(time.strftime('%H:%M'))  # format time to hours and minutes and change type to string
        
        # schedule = {'name': 'topic', 'duration': duration, 'start': start, 'end': end}  # creating a new dictionary
        schedule = {'duration': duration, 'start': start, 'end': end}  # creating a new dictionary for a topic
        scheduleList.append(schedule)  # appending the new dictionary to the list
    
    return scheduleList


def convertToTime(stringTime):  # to convert a string to time
    string = stringTime.split(':')  # splitting the string to separate hours from minutes

    hours = int(string[0])  # getting the hours as an int
    minutes = int(string[1])  # getting the minutes as an int
    
    finalTime = timedelta(hours=hours, minutes=minutes)  # creating a timedelta from the information we got
    
    return finalTime

    
def calcEnd(time, topicduration): # calculating the end time of a topic
    endTime = time + topicduration # adding the duration of the topic to the current time
    
    return endTime


def calcMaxDuration(starttime, endtime):  # calculating the max duration of a topic. It depends on the start time and end time
    calc = convertToTime(endtime) - convertToTime(starttime)  # getting the difference

    maxDuration = int((calc.total_seconds()) / 60)  # converting to int and minutes
    
    return maxDuration


def getModule(guid):  # get a module from Xyleme
    # connecting to xyleme
    xh = XylemeHelper(os.environ["XYLEME_USERNAME"], os.environ["XYLEME_PASSWORD"])
    xh.login()
    
    ssp_guid = guid
    ssp = xh.get_ssp_raw(ssp_guid)
    
    return ssp


def convertToDict(module):  # converting module gotten as xml to a dict
    doc = xmltodict.parse(module, force_list={'Topic', 'Module', 'Lesson'})
    
    return dict(doc)


def createDict(module):
    convertedModule = convertToDict(module)

    finaldict = []  # creating an empty list
    lessonDict = {}  # creating an empty dictionary

    name = convertedModule['IA']['CoverPage']['Title']  # getting the name of a module
    
    for modules in convertedModule['IA']['Modules']['Module']:  # looping through the modules
        lessons = []  # creating an empty list for the lessons
        for lesson in modules["Lesson"]:  # looping through the lessons
            topics = []  # creating an empty list for the topics
            for topic in lesson['Topic']:  # looping through the topics
                topics.append({'title': topic['Title']})  # appending the title of the topic to the list as a dictionary
        
            lessons.append({'title': lesson['Title'], 'topics': topics})  # appending the list of topics to the lessons
            
        finaldict.append({'title': modules['Title'], 'lessons': lessons})  # appending the lesson to the list
        
    addCourse(name, finaldict)