from pyspark import SparkContext
from functions import *
import re
import json

sc = SparkContext("local", "Simple App")
setDefaultAnswer(sc.parallelize([0]))

## Load data into RDDs
playRDD = sc.textFile("datafiles/play.txt")
logsRDD = sc.textFile("datafiles/NASA_logs_sample.txt")
amazonInputRDD = sc.textFile("datafiles/amazon-ratings.txt")
nobelRDD = sc.textFile("datafiles/prize.json")

## The following converts the amazonInputRDD into 2-tuples with integers
amazonBipartiteRDD = amazonInputRDD.map(lambda x: x.split(" ")).map(lambda x: (x[0], x[1])).distinct()


### Task 1
print "=========================== Task 1"
task1_result = task1(playRDD)


textRDD = playRDD.flatMap(lambda line: line.split("\n"))  # split the text by line
longLine = textRDD.filter(lambda line: len(line.split( )) > 10)
task1_result= longLine.map(lambda line: (line, len(line.split(" "))))
for x in task1_result.takeOrdered(10):
	print x


### Task 2
print "=========================== Task 2"
#result = nobelInfo.flatMap(lambda x:x['laureates'])
#surnames = result.map(lambda x:x['surname'])
task2_result = nobelRDD.map(json.loads).flatMap(lambda x:x['laureates']).map(lambda x:x['surname']).distinct()
#task2_result = nobelRDD.map(json.loads).flatMap(task2_flatmap).distinct()
print task2_result.takeOrdered(10)

#### Task 3
print "=========================== Task 3"
nobelRDD.map(json.loads).flatMap(lambda x:[(x['category'],i['surname']) for i in x['laureates']]).distinct()
#result = nobelInfo.map(lambda x: (x['category'],x['laureates']))
result = nobelRDD.map(json.loads).map(lambda x: (x['category'],x['laureates'])).map(lambda x:[(x[0],x[1][i]['surname']) for i in range(0,len(x[1]))])
#task3_result = result.reduceByKey(lambda x,y: x+ "," +y)
task3_result = result.groupByKey().mapValues(list)

task3_result = task3(nobelRDD)
for x in task3_result.takeOrdered(10):
	print x

#### Task 4
print "=========================== Task 4"
parts = logsRDD.map(lambda x: x.split()).takeOrdered(2)

time = logsRDD.map(lambda x: x.split()).map(lambda x: x[3])
#result = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3]))
result = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3][1:12]))   # get host, and date

#host1 = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3][1:12])).filter(lambda x:x[1] in ['01/Jul/1995'])
#host2 = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3][1:12])).filter(lambda x:x[1] in ['02/Jul/1995'])
#visitall = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3][1:12])).distinct().groupByKey().mapValues(list)
visitall = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3][1:12])).distinct().groupByKey().mapValues(list).filter(lambda x:x[1] == ['01/Jul/1995', '02/Jul/1995'] or x[1] ==['02/Jul/1995','01/Jul/1995'])
task4_result = visitall.map(lambda x:x[0])

----
visitall = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3][1:12])).distinct().groupByKey().mapValues(list).map(lambda x:(x[0],sorted(x[1]))).filter(lambda x:x[1] == ['01/Jul/1995', '02/Jul/1995'])
task4_result = visitall.map(lambda x:x[0])   #get host

task4_result = task4(logsRDD, ['01/Jul/1995', '02/Jul/1995'])
for x in task4_result.takeOrdered(10):
	print x

#### Task 5
print "=========================== Task 5"
numofP = amazonInputRDD.map(lambda x: x.split(" ")).map(lambda x: (x[0], x[1])).distinct().groupByKey().mapValues(len).map(lambda x: (x[1],x[0]))
task5_result =  numofP.groupByKey().mapValues(len)

task5_result = task5(amazonBipartiteRDD)
print task5_result.collect()

#### Task 6
print "=========================== Task 6"

#logsEnd = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0],x[6])).distinct().groupByKey().mapValues(list)

visitFirstDay = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3][1:12],x[6])).filter(lambda x:x[1] == '01/Jul/1995')
visitSecondDay = logsRDD.map(lambda x: x.split()).map(lambda x:(x[0], x[3][1:12],x[6])).filter(lambda x:x[1] == '02/Jul/1995')
Second = visitSecondDay.map(lambda x:(x[0],x[2]))
First = visitFirstDay.map(lambda x:(x[0],x[2]))
r = First.cogroup(Second)
final = r.filter(lambda (x,y):list(y[0])!= [] and list(y[1])!= [])
task6_result = final.map(lambda (x,y):(x, (list(y[0]),list(y[1]))))

#def parseApacheLogLine(logline):
    """ Parse a line in the Apache Common Log format
    Args:
        logline (str): a line of text in the Apache Common Log format
    Returns:
        tuple: either a dictionary containing the parts of the Apache Access Log and 1,
               or the original invalid log line and 0
    """
    '''APACHE_ACCESS_LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+)\s*(\S*)" (\d{3}) (\S+)'
    match = re.search(APACHE_ACCESS_LOG_PATTERN, logline)
    if match is None:
        return (logline, 0)
    size_field = match.group(9)
    if size_field == '-':
        size = long(0)
    else:
        size = long(match.group(9))
    return (Row(
        host          = match.group(1),
        client_identd = match.group(2),
        user_id       = match.group(3),
        date_time     = parse_apache_time(match.group(4)),
        method        = match.group(5),
        endpoint      = match.group(6),
        protocol      = match.group(7),
        response_code = int(match.group(8)),
        content_size  = size
    ), 1)'''

'''def endpoint(logline):
	match = re.search('(\S+) (\S+)\s*(\S*) ', logline)
	if match is not None:
		return match.group(1)
	else:
		return None'''

task6_result = task6(logsRDD, '01/Jul/1995', '02/Jul/1995')
for x in task6_result.takeOrdered(10):
	print x

#### Task 7
print "=========================== Task 7"


motivation = nobelRDD.map(json.loads).flatMap(lambda x:x['laureates']).filter(lambda x:'motivation' in x).map(lambda x:x['motivation'])
bigrams = motivation.map(lambda s : s.split(" ")).flatMap(lambda s: [((s[i],s[i+1]),1) for i in range (0, len(s)-1)])
counts = bigrams.reduceByKey(lambda x,y: x+y)



task7_result = task7(nobelRDD)
for x in task7_result.takeOrdered(10):
	print x

#### Task 8 -- we will start with a non-empty currentMatching and do a few iterations
print "=========================== Task 8"
currentMatching = sc.parallelize([('user1', 'product8')])
res1 = task8(amazonBipartiteRDD, currentMatching)
print "Found {} edges to add to the matching".format(res1.count())
print res1.takeOrdered(100)
currentMatching = currentMatching.union(res1)
res2 = task8(amazonBipartiteRDD, currentMatching)
print "Found {} edges to add to the matching".format(res2.count())
print res2.takeOrdered(100)
currentMatching = currentMatching.union(res2)


------------------------------>

currentUlist = currentMatching.map(lambda x: x[0]).distinct().collect()
currentPlist = currentMatching.map(lambda x: x[1]).distinct().collect()


#2
r1 = amazonBipartiteRDD.groupByKey().mapValues(list).map(lambda x: (x[0],sorted(x[1]))).filter(lambda x:x[0] not in currentUlist).map(lambda x:(x[0],sorted(x[1])))
#newMatch = r1.filter(lambda x: x[1][0] not in currentPlist).map(lambda x:(x[0],x[1][0]))
#r2 = amazonBipartiteRDD.map(lambda x:(x[1],x[0])).distinct().groupByKey().mapValues(list).filter(lambda x:x[0] not in currentPlist).map(lambda x:(x[0],sorted(x[1])))
#newMatch2 = r2.filter(lambda x:x[1][0] not in currentUlist).map(lambda x:(x[0],x[1][0]))
def productsnotMatched(a,currentPlist):
	notMatchedP = []
	for i in a:
		if i not in currentPlist:
			notMatchedP.append(i)
	return notMatchedP 
unmatched = r1.map(lambda x:(x[0],productsnotMatched(x[1],currentPlist)))
newMatch = unmatched.filter(lambda x:x[1]!= []).map(lambda x:(x[0], min(x[1])))

some = newMatch.map(lambda x:(x[1],x[0])).groupByKey().mapValues(list).map(lambda x:(x[0],min(x[1]))).map(lambda x:(x[1],x[0]))

currentMatching.union(some)
'''r2 = amazonBipartiteRDD.map(lambda x:(x[1],x[0])).groupByKey().mapValues(list).map(lambda x:(x[0],sorted(x[1]))).filter(lambda x:x[0] not in currentPlist)
def usersnotMatched(a,currentUlist):
	notMatchedP = []
	for i in a:
		if i not in currentUlist:
			notMatchedP.append(i)
	return notMatchedP 
unmatched2 = r2.map(lambda x:(usersnotMatched(x[1],currentUlist),x[0]))
newMatch2 = unmatched2.map(lambda x:(min(x[0]),x[1]))






