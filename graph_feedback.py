import string
import csv
import math
from datetime import datetime,timedelta
from sklearn.ensemble import RandomForestClassifier
import sklearn.cross_validation as skcv
import sklearn.metrics as skmet
import sklearn.grid_search as skgs
import numpy as np




def get_apple_data():
    f = open('./Financial_data/ibmBluemix_rated_data_apple.txt','r')
    list = f.readline()
    f.close()
    print list
    result = string.split(list,"],[")
    parsed_list = []

    for x in range(1,len(result)-1):
        splitting = string.split(result[x],",")
        date = splitting[0]
        url  = splitting[1]
        url_sent = int(splitting[2])

        apple_sent = int(splitting[3])
        apple_rel = float(splitting[4])

        new_elem = [date,url,url_sent,apple_sent,apple_rel]

        parsed_list = parsed_list + [new_elem]


    #print parsed_list

    used_dates = []
    averaged_date_list = []

    item_count = 0
    dump_1 = 0
    dump_2 = 0
    dump_3 = 0
    firstTry = True

    for x in parsed_list:
        #check if x.date is in used_dates: if yes: keep averaging
        if(x[0] not in used_dates):
            #process old dump
            if(not firstTry):
                dump_1_avg = dump_1 / (item_count*1.0)
                dump_2_avg = dump_2 / (item_count*1.0)
                dump_3_avg = dump_3 / (item_count*1.0)
                corr_date = used_dates[len(used_dates)-1]
                averaged_date_list = averaged_date_list + [[dump_1_avg,dump_2_avg,dump_3_avg]]
            else:
                firstTry = False

            used_dates = used_dates + [x[0]]
            item_count = 1
            dump_1 = x[2]
            dump_2 = x[3]
            dump_3 = x[4]

        else:
            dump_1 = dump_1 + x[2]
            dump_2 = dump_2 + x[3]
            dump_3 = dump_3 + x[4]
            item_count = item_count + 1

    #last dump
    dump_1_avg = dump_1 / (item_count*1.0)
    dump_2_avg = dump_2 / (item_count*1.0)
    dump_3_avg = dump_3 / (item_count*1.0)
    corr_date = used_dates[len(used_dates)-1]
    averaged_date_list = averaged_date_list + [[dump_1_avg,dump_2_avg,dump_3_avg]]

    return averaged_date_list

def get_actual_tendency(start_date,amount_days=7):
    start_date_ = datetime.strptime(start_date, "%Y-%m-%d")
    start_date_ = start_date_.date()
    with open('./Financial_data/apple.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        relevant_graph_data = []
        for row in reader:
            date=datetime.strptime(row[0], "%Y-%m-%d")
            date = date.date()
            if date > start_date_ and date < start_date_ + timedelta(minutes=1, hours=amount_days*24, seconds=59):
                relevant_graph_data.append([date,float(row[1])])
        first = relevant_graph_data[0][1]
        last = relevant_graph_data[-1][1]
        delta = last - first        # y-delta (GK)
        tan = delta / amount_days   # tan = GK / AK
        if tan > 0.2:
            result = 2
        elif tan < -0.2:
            result = 0
        else:
            result = 1
        print start_date
        print math.atan(tan)
    return result

def score(gtruth, gpred):
    # Minimizing this should result in minimizing sumscore in the end.
    # We do not actually need the len(gtruth), but it enhances debugging, since it then corresponds to the sumscore.
    return float(np.sum(gtruth != gpred))/(len(gtruth))


def forest_classifier(Xtrain, Ytrain):
    param_grid = {'n_estimators': range(1, 100, 25), 'min_samples_split': range(1,4,1), 'max_depth': range(1,100,30)}
    classifier = RandomForestClassifier(n_jobs=-1,verbose=1, max_depth=None,min_samples_split=1)
    classifier.fit(Xtrain, Ytrain)
    print 'FOREST: classifier: ', classifier
    print 'FOREST: classifier.score: ', score(Ytrain, classifier.predict(Xtrain))
    scorefun = skmet.make_scorer(lambda x, y: -score(x, y))
    grid_search = skgs.GridSearchCV(classifier, param_grid, scoring=scorefun, cv=3)
    grid_search.fit(Xtrain, Ytrain)
    print 'FOREST: best_estimator_: ', grid_search.best_estimator_
    print 'FOREST: best_estimator_.score: ', score(Ytrain, grid_search.predict(Xtrain))
    return grid_search.best_estimator_

def main():
    start = datetime.strptime("2016-02-29", "%Y-%m-%d")
    res = []
    for i in range(1,47):
        res.append(get_actual_tendency(str(start.date()),7))
        start = start - timedelta(minutes=59, hours=23, seconds=0)
    lables =  res
    learn_data =  get_apple_data()
    print learn_data
    classifier = forest_classifier(learn_data,lables)


if __name__ == "__main__":
    main()