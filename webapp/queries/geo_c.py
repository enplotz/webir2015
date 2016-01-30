import math
initData = 'SELECT o.id, o.name,  o.lat,o.lng FROM org o WHERE o.lng!=48.6618471 AND o.lat!=9.0036649'

def getEdgeData(orgid):
    return 'SELECT * FROM co_helper WHERE org=\'' + orgid +'\''

def getSugg(t):
    return 'SELECT name AS label, id AS value FROM org WHERE name LIKE \'%'+t+'%\' LIMIT 5'

def getClosest(lat,lon,zoom, selected):
    maxDist = 156543.03392 * math.cos(lat * math.pi / 180) / math.pow(2, zoom)
    maxDist /= 5000

    q = 'SELECT CASE WHEN org1 IN ('+selected+') THEN org2 ELSE org1 END AS id FROM '
    q+= '(SELECT *, ST_Distance(ST_MakePoint('+str(lat)+','+str(lon)+'),path) AS dist FROM geodesics WHERE '
    q+= '(org1 IN (' + selected +') OR org2 IN (' + selected +'))) a  WHERE dist <'+str(maxDist) + ' ORDER BY dist ASC LIMIT 1';
    print q
    return q