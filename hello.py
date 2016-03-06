"""Cloud Foundry test"""
from flask import Flask, json
from datetime import datetime,timedelta
import time
import os
import csv
from flask.ext.cors import CORS
app = Flask(__name__)
cors = CORS(app, resources={r"*": {'origins': '*',
                                   'headers': 'content-type',
                                   'methods': 'GET, PUT, POST, DELETE'}})


# On Bluemix, get the port number from the environment variable VCAP_APP_PORT
# When running this app on the local machine, default the port to 8080
port = int(os.getenv('VCAP_APP_PORT', 8080))

@app.route('/get_graph_data/<string:id>/<string:start>/<string:end>',methods=['POST','GET'])
@app.route('/get_graph_data/<string:id>')
@app.route('/get_graph_data',methods=['GET'])
def get_graph_data(id='vw',start='01-02-16',end='29-02-16'):
    csv_file = ""
    start_=datetime.strptime(start, "%d-%m-%y")
    end_=datetime.strptime(end, "%d-%m-%y")+timedelta(minutes=59, hours=23, seconds=59)
    #print start_
    #print end_
    if id == 'vw':
        csv_file = 'vw.csv'
    elif id == 'ubs':
    	csv_file = 'ubsn.csv'
    elif id == 'apple':
    	csv_file = 'apple.csv'
    elif id == 'nestle':
    	csv_file = 'nestle.csv'
    elif id == 'boeing':
    	csv_file = 'boeing.csv'
    graph_data = []
    with open('./Financial_data/'+csv_file, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        y = []
        x = []
        for row in reader:
            y.append(float(row[1]))
            date=datetime.strptime(row[0], "%Y-%m-%d")
            print date.isoformat()
            epoch = date_time_milis = time.mktime(date.timetuple()) * 1000 + date.microsecond / 1000
            graph_data.append([epoch,float(row[1])])

        #pyplot.savefig('example01.png')
        #pyplot.plot(range(0,len(y)),y)
        #pyplot.show()
        csvfile.close()
    return json.dumps(graph_data)

@app.route('/')
def default():
    return 'Hi there!'

@app.route('/get_rating/<string:data_id>/<int:days>',methods=['POST','GET'])
@app.route('/get_rating/',methods=['POST','GET'])
def get_rating(data_id='vw',days=14):
    #define the size of the day frame to look back for each day
    day_frame_size = days

    #define todays date
    today = datetime.strptime("29/02/16","%d/%m/%y")

    #open and read the input file
    if data_id == 'vw':
        filename = './ML_data/vw_news.txt'
    inputfile  = open(filename)
    input_text = inputfile.readlines()

    #initially fill the day frame array
    frame_array = []
    last_date_raw = input_text[len(input_text)-1]
    last_date = datetime.strptime(last_date_raw.strip(),"%d/%m/%y")

    #build up overall table
    counting_date = today
    while(counting_date != last_date):
        frame_array = frame_array + [[counting_date,[]]]
        counting_date = counting_date - timedelta(1)
    frame_array = frame_array + [[counting_date,[]]]

    nr_of_entries = len(input_text)/3
    for entry_index in range(0,nr_of_entries):
        rating      = input_text[3*entry_index+1].strip()
        date_str    = input_text[3*entry_index+2].strip()
        parsed_date = datetime.strptime(date_str,"%d/%m/%y")
        day_diff = (today-parsed_date).days

        currList = frame_array[day_diff][1]
        currList = currList + [rating]
        frame_array[day_diff][1] = currList

    result = []

    last_feasible_date = counting_date + timedelta(day_frame_size)
    for i in range(0,len(frame_array)):
        entry_date = frame_array[i][0]

        rating_values = []
        for j in range(0,day_frame_size):
            rating_values = rating_values + frame_array[i+j][1]

        rating = None
        if(len(rating_values) > 0):
            rating = get_rating_from_array(rating_values)

        result = result + [[frame_array[i][0],rating]]

        #this was the last date we can have some data for
        if(entry_date == last_feasible_date):
            break

    return json.dumps(result[0][1])


#calculate an overall rating from an array of rating values like ["0","2","2","1",...] -> 0.231
def get_rating_from_array(value_array):
    nr_0 = 0
    nr_1 = 0
    nr_2 = 0

    for entry in value_array:
        if(entry == "0"): nr_0 = nr_0 + 1
        if(entry == "1"): nr_1 = nr_1 + 1
        if(entry == "2"): nr_2 = nr_2 + 1

    overall_rating = (0.0*nr_0 + 0.5*nr_1 + nr_2)/(nr_0+nr_1+nr_2)

    return overall_rating


if __name__ == "__main__":
	app.run(host='0.0.0.0',port=port)
