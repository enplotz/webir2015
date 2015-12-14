from os import environ
from os.path import join, dirname

from dotenv import load_dotenv
from flask import Blueprint, render_template, redirect, url_for, request
from flask import Flask, jsonify
from flask.ext.cache import Cache
from flask_bootstrap import Bootstrap
from flask_debug import Debug
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy_session import flask_scoped_session
from sqlalchemy import create_engine, String
from sqlalchemy import func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import cast

from queries.dashboard import avg_cite_sql,top_authors_m, time_series
import queries.co_network as co

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config.from_object(environ['APP_SETTINGS'])
Bootstrap(app)
Debug(app)
# Check Configuring Flask-Cache section for more details
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

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

# Cache for x seconds
@cache.cached(timeout=60)
def get_metrics():
    return {
        'num_authors': session.query(Author).count(),
        'num_authors_fully': session.query(Author).filter(Author.measures.isnot(None)).count(),
        'num_documents': session.query(Document).count(),
        'num_fields': session.query(Label).count(),
    }

@app.route('/test', methods=['GET'])
def test():
    return render_template('pages/index.html')

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
        ranks = session.execute(top_authors_m(1,10))
        series_docs = session.execute(time_series(False))
        series_cites = session.execute(time_series(True))
        metrics = get_metrics()
        num_authors = session.query(func.count(Author.id)).scalar()
        print("Num authors %d " % num_authors)

    except Exception as e:
        errors.append(e)
        return render_template('pages/index.html', errors=errors, rankings=ranks, metrics=None)

    return render_template('pages/index.html', errors=errors, rankings=ranks, metrics=metrics, num_authors=num_authors)


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
    except Exception as e:
        errors.append(e)
        return render_template('pages/researcher.html', errors=errors)

    return render_template('pages/researcher.html', researcher=res, publications=pub)


@app.route('/researcher/<id>/fos/<field_name>')
def compare_researcher_fos(id, field_name):
    errors = []
    results = {}
    try:
        res = session.query(Author).get(id)
        avg = session.execute(avg_cite_sql([field_name])).fetchone()
    except Exception as e:
        errors.append(e)
        return render_template('pages/compare.html', errors=errors)
    return render_template('pages/compare.html', researcher=res, avg=avg, field_name=field_name)


def show_search_form(entity_name, action):
    return render_template('search_entity.html', entity_name=entity_name, action=action)


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

if __name__ == '__main__':
    # print(environ['APP_SETTINGS'])
    app.run(host='0.0.0.0', port=5000)
