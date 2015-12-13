from flask import Flask, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, String
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects import postgresql
from flask_bootstrap import Bootstrap
from flask import Blueprint, render_template, flash, redirect, url_for,jsonify, request
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape
from os.path import join, dirname
from dotenv import load_dotenv
from os import environ
from flask_debug import Debug
from queries.dashboard import MOST_CITED_BY_FIELD, avg_cite_sql,top_authors_m, time_series

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = Flask(__name__)
app.config.from_object(environ['APP_SETTINGS'])

Bootstrap(app)
Debug(app)

frontend = Blueprint('frontend', __name__)
app.register_blueprint(frontend)

Base = automap_base()
engine = create_engine(app.config['SQL_ALCHEMY_DATABASE_URI'])
Base.prepare(engine, reflect=True)
Author = Base.classes.authors
Document = Base.classes.documents
Label = Base.classes.labels

toolbar = DebugToolbarExtension(app)

@app.route('/', methods=['GET'])
def index():
    errors = []
    ranks = []
    series_docs = []
    series_cites = []

    # Dashboard
    # Top-Researcher by Field (cited)
    # Max-Cites by Field
    # Avg # Cites by Field
    try:
        session = Session(engine)
        try:
            ranks = session.execute(top_authors_m(1,10))
            series_docs = session.execute(time_series(False))
            series_cites = session.execute(time_series(True))

        finally:
            session.close()
    except Exception as e:
        errors.append(e)
        return render_template('index.html', errors=errors,rankings=ranks)
    return render_template('index.html', rankings= ranks, errors= errors)


def field_term(search_term):
    return '_'.join(search_term.lower().split(' '))

@app.route('/getRankings/<m>', methods=['GET', 'POST'])
def getRankings(m):
    errors = []
    result = []
    try:
        session = Session(engine)
        try:
            result = session.execute(top_authors_m(int(m),10))
        finally:
            session.close()
    except Exception as e:
        errors.append(e)
    return jsonify(results = [dict(row) for row in result], errors =errors)

@app.route('/getTimeSeries', methods=['GET','POST'])
def getTimeSeries():
    errors = []
    results= []
    try:
        session = Session(engine)
        try:
            docCounts = session.execute(time_series(False))
            citeCounts = session.execute(time_series(True))
            results = [[dict(row) for row in docCounts], [dict(row) for row in citeCounts]]
        finally:
            session.close()
    except Exception as e:
        errors.append(e)
    return jsonify(results = results, errors =errors)



@app.route('/search', methods=['GET', 'POST'])
def search():
    errors = []
    if request.method == 'POST':
        search_term = request.form['entity_value']
        # print(search_term)
        fos_search_term = field_term(search_term)
        try:
            session = Session(engine)
            res = None
            fields = None
            try:
                res = session.query(Author).filter(Author.name.like('%' + search_term + '%')).all()
                fields = session.query(Label).filter(Label.field_name.like('%' + fos_search_term + '%')).all()
            finally:
                session.close()
            return render_template('search_result.html', researchers=res, search_term=search_term,
                                   fos_search_term=fos_search_term, fields=fields)
        except Exception as e:
            errors.append(e)

    return render_template('search_entity.html', entity_name='Researcher or Field', action='/search', errors=errors)


@app.route('/researcher', methods=['GET'])
def find_researcher():
    return redirect(url_for('search'), 302)
    # if request.method == 'POST':
    #     researcher = request.form['entity_value']
    #     return redirect(url_for('show_researcher_profile', id=researcher))
    # return show_search_form('Researcher', '/researcher')


@app.route('/researcher/<id>')
def show_researcher_profile(id):
    errors = []
    results = {}
    try:
        # QUERY FOR AUTHORS HAVING THE FOS
        session = Session(engine)
        try:
            res = session.query(Author).get(id)
            pub = session.query(Document).filter(Document.author_id == id).all()
        finally:
            session.close()
    except Exception as e:
        errors.append(e)
        return render_template('researcher.html', errors=errors)

    return render_template('researcher.html', researcher=res, publications=pub)


@app.route('/researcher/<id>/fos/<field_name>')
def compare_researcher_fos(id, field_name):
    errors = []
    results = {}
    try:
        session = Session(engine)
        try:
            res = session.query(Author).get(id)
            avg = session.execute(avg_cite_sql([field_name])).fetchone()
            # print(avg)
        finally:
            session.close()
    except Exception as e:
        errors.append(e)
        return render_template('compare.html', errors=errors)

    return render_template('compare.html', researcher=res, avg=avg, field_name=field_name)


def show_search_form(entity_name, action):
    return render_template('search_entity.html', entity_name=entity_name, action=action)


@app.route('/fos', methods=['POST', 'GET'])
def find_field():
    # if request.method == 'POST':
    #     fos = field_term(request.form['entity_value'])
    #     return redirect(url_for('show_field', field_name=fos))
    # return show_search_form('Field Of Study', '/fos')
    return redirect(url_for('search'), 302)


@app.route('/fos/<field_name>')
def show_field(field_name):
    errors = []
    results = {}
    try:
        # QUERY FOR AUTHORS HAVING THE FOS
        session = Session(engine)
        try:
            res = session.query(Author).filter(
                Author.fields_of_study.contains(cast([field_name], postgresql.ARRAY(String)))).all()
        finally:
            session.close()
    except Exception as e:
        errors.append(e)
        return render_template('fos.html', errors=errors)

    # print('Got {0} results.'.format(len(res)))
    return render_template('fos.html', results=res, field_of_study=field_name)


if __name__ == '__main__':
    # print(environ['APP_SETTINGS'])
    app.run(host='0.0.0.0', port=5000)
