import time
from datetime import datetime
from os import environ

import requests
from flask import Blueprint, render_template, redirect, url_for, request, Response
from flask import Flask
from flask import jsonify, abort
from flask.ext.cache import Cache
from flask_bootstrap import Bootstrap
from flask_debug import Debug
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine, String
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import cast

import queries.co_network as co
from queries.dashboard import avg_measures_sql,top_authors_m, time_series_documents, time_series_cited

# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)

app = Flask(__name__)
app.config.from_object(environ['APP_SETTINGS'])
# app.config.from_object(conf)
Bootstrap(app)
Debug(app)

# Check Configuring Flask-Cache section for more details
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

frontend = Blueprint('frontend', __name__)
app.register_blueprint(frontend)

Base = automap_base()
engine = create_engine(app.config['SQL_ALCHEMY_DATABASE_URI'])
Base.prepare(engine, reflect=True)

# TODO make base classes use the correct engine
# Currently, this uses sqlite o.O: `num_authors = Author.query.count()`
Author = Base.classes.authors
Document = Base.classes.documents
Label = Base.classes.labels

toolbar = DebugToolbarExtension(app)

# Enable SQLAlchemy in Debug Toolbar without flask-sqlalchemy :)
from flask.ext.sqlalchemy import _EngineDebuggingSignalEvents
_EngineDebuggingSignalEvents(engine, app.import_name).register()

session_factory = sessionmaker(bind=engine)
session = flask_scoped_session(session_factory, app)

# From http://flask.pocoo.org/snippets/33/
@app.template_filter()
def friendly_time(dt, past_="ago",
    future_="from now",
    default="just now"):
    """
    Returns string representing "time since"
    or "time until" e.g.
    3 days ago, 5 hours from now etc.
    """

    now = datetime.now()
    if now > dt:
        diff = now - dt
        dt_is_past = True
    else:
        diff = dt - now
        dt_is_past = False

    periods = (
        (diff.days / 365, "year", "years"),
        (diff.days / 30, "month", "months"),
        (diff.days / 7, "week", "weeks"),
        (diff.days, "day", "days"),
        (diff.seconds / 3600, "hour", "hours"),
        (diff.seconds / 60, "minute", "minutes"),
        (diff.seconds, "second", "seconds"),
    )

    for period, singular, plural in periods:

        if period:
            return "%d %s %s" % (period, \
                singular if period == 1 else plural, \
                past_ if dt_is_past else future_)

    return default

# Cache for x seconds
@cache.cached(timeout=30, key_prefix='get_metrics')
def get_metrics():
    # Use func.count to only count ids
    return {
        'num_authors': session.query(func.count(Author.id)).scalar(),
        'num_authors_fully': session.query(Author).filter(Author.measures.isnot(None)).count(),
        'num_documents': session.query(func.count(Document.id)).scalar(),
        'num_fields': session.query(func.count(Label.field_name)).scalar(),
    }

@cache.cached(timeout=30, key_prefix='get_rankings')
def rankings():
    top_q = top_authors_m(1,10)
    ts_docs_q = time_series_documents()
    ts_cites = time_series_cited()
    return {
        'ranks': session.execute(top_q).scalar(),
        'series_doc': session.execute(ts_docs_q).scalar(),
        'series_cities': session.execute(ts_cites).scalar()
    }

@app.route('/', methods=['GET'])
def index():
    errors = []
    ranks = []
    series_docs = []
    series_cites = []
    metrics = None

    # Dashboard
    # Top-Researcher by Field (cited)
    # Max-Cites by Field
    # Avg # Cites by
    try:
        r = rankings()
        ranks = r['ranks']
        series_doc = r['series_doc']
        series_cities = r['series_cities']
        metrics = get_metrics()
        # num_authors = session.query(func.count(Author.id)).scalar()
    except Exception as e:
        errors.append(e)
        return render_template('pages/index.html', errors=errors, rankings=ranks, metrics=None)
    return render_template('pages/index.html', errors=errors, rankings=ranks, metrics=metrics, num_authors=metrics['num_authors'])


@app.route('/compare', methods=['POST', 'GET'])
def compare_authors():
    # This route should enable the user to compare n authors.
    # We have to start a crawling job
    # wait until it is finished
    # redirect to a new/the same page and display the results
    pass


@app.route('/yield')
def yield_test():
    def inner():
        for x in range(100):
            time.sleep(1)
            yield '%s<br/>\n' % x
    return Response(inner(), mimetype='text/html')

def field_term(search_term):
    return '_'.join(search_term.lower().split(' '))


@app.route('/getRankings/<m>', methods=['GET', 'POST'])
def getRankings(m):
    errors = []
    result = []
    try:
        result = session.execute(top_authors_m(int(m),10))
    except Exception as e:
        errors.append(e)
    return jsonify(results = [dict(row) for row in result], errors =errors)


@app.route('/getTimeSeries', methods=['GET','POST'])
def getTimeSeries():
    errors = []
    results= []
    try:
        docCounts = session.execute(time_series(False))
        citeCounts = session.execute(time_series(True))
        results = [[dict(row) for row in docCounts], [dict(row) for row in citeCounts]]
    except Exception as e:
        errors.append(e)
    return jsonify(results = results, errors =errors)



@app.route('/search', methods=['GET', 'POST'])
def search():
    errors = []
    if request.method == 'POST':
        search_term = request.form['entity_value']
        fos_search_term = field_term(search_term)
        print 'Getting %s' % fos_search_term
        try:
            authors = session.query(Author).filter(Author.name.like('%' + search_term + '%')).all()
            fields = session.query(Label).filter(Label.field_name.like('%' + fos_search_term + '%')).all()
            return render_template('pages/search/result.html',
                                   search_term=search_term,
                                   fos_search_term=fos_search_term,
                                   fields=fields,
                                   researchers=authors
                                   )
        except Exception as e:
            errors.append(e)
    return render_template('pages/search/entity.html', entity_name='Researcher or Field', action='/search', errors=errors)


@app.route('/researchers', methods=['GET'])
def researchers():
    errors = []
    try:
        res = session.query(Author).all()
        return render_template('pages/researchers.html', researchers=res)
    except Exception as e:
        errors.append(e)
    return render_template('pages/researchers.html', errors=errors)


@app.route('/researcher', methods=['GET'])
def find_researcher():
    return redirect(url_for('search'), 302)


@app.route('/researcher/<id>')
def show_researcher_profile(id):
    errors = []
    results = {}
    try:
        res = session.query(Author).get(id)
        pub = session.query(Document).filter(Document.author_id == id).all()
        print 'Num Publications: %d' % len(pub)
        print 'Researcher: %s' % res.id if res else None
        if not res:
            abort(404)
    except Exception as e:
        errors.append(e)
        return render_template('pages/researcher.html', errors=errors, researcher=None, header="Researcher Profile")

    return render_template('pages/researcher.html', researcher=res, publications=pub, header="Researcher Profile")


@app.route('/researcher/<id>/fos/<field_name>')
def compare_researcher_fos(id, field_name):
    errors = []
    results = {}
    try:
        print field_name
        res = session.query(Author).get(id)
        print "Researcher %s" % res.name if res else None
        avg = session.execute(avg_measures_sql([field_name])).fetchone()
        print "Avg: %s " % avg
        return render_template('pages/compare.html', errors=errors, researcher=res, avg=avg, field_name=field_name)
    except Exception as e:
        errors.append(e)
        print e
    return render_template('pages/compare.html', errors=errors, field_name=field_name)



@app.route('/fields', methods=['GET'])
def fields():
    errors = []
    try:
        res = session.query(Label).all()
        return render_template('pages/fields.html', fields=res)
    except Exception as e:
        errors.append(e)
        print e
    return render_template('pages/fields.html', errors=errors)


@app.route('/fos', methods=['POST', 'GET'])
def find_field():
    return redirect(url_for('search'), 302)


@app.route('/fos/<field_name>')
def show_field(field_name):
    errors = []
    results = {}
    try:
        res = session.query(Author).filter(
            Author.fields_of_study.contains(cast([field_name], postgresql.ARRAY(String)))).all()
    except Exception as e:
        errors.append(e)
        return render_template('pages/fos.html', errors=errors)
    return render_template('pages/fos.html', results=res, field_of_study=field_name)


@app.route('/documents', methods=['GET'])
def documents():
    errors = []
    try:
        res = session.query(Document).all()
        return render_template('pages/documents.html', documents=res)
    except Exception as e:
        errors.append(e)
        print e
    return render_template('pages/documents.html', errors=errors)


@app.teardown_request
def teardown_request(exception):
    if exception:
        session.rollback()
        session.remove()
    session.remove()

# co author networks:


@app.route('/co/EntityByID/<i>',  methods=['POST', 'GET'])
def getEntityById(i):
    errors = []
    results = []
    try:
        ent = session.execute(co.getEntity(i))
        results  = [dict(row) for row in ent]
    except Exception as e:
        errors.append(e)
    return jsonify(results = results, errors =errors)


@app.route('/co/getExtended',  methods=['POST', 'GET'])
def getExtended():
    errors = []
    results = []
    try:
        all =  request.form['all']
        clicked = request.form['clicked']

        limit = request.form['limit']
        print "all" + all
        print "clicked" + clicked
        print "limit" + limit
        ent = session.execute(co.getExtended(clicked, [all], limit))
        results  = [dict(row) for row in ent]
    except Exception as e:
        errors.append(e)
    return jsonify(results = results, errors =errors)


@app.route('/schedule', methods=['POST'])
def schedule_spider():
    # project
    project = request.form['project']
    # get spider name
    spider_name = request.form['spider']
    # and start_author for test for now
    start_authors = request.form['start_authors']
    r = requests.post('http://localhost:6800/schedule.json',
                      data={'project': project, 'spider': spider_name, 'start_authors': start_authors})
    return Response(
            r.text,
            status=r.status_code,
            content_type=r.headers['content-type']
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
