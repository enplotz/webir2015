from flask import Flask, render_template, request
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, String
from sqlalchemy.sql.expression import cast
from sqlalchemy.dialects import postgresql

from flask_bootstrap import Bootstrap

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from markupsafe import escape

from os.path import join, dirname
from dotenv import load_dotenv
from os import environ

from flask_debug import Debug

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
Labels = Base.classes.labels

toolbar = DebugToolbarExtension(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}

    return render_template('index.html')

@app.route('/researcher', methods=['POST', 'GET'])
def find_researcher():
    if request.method == 'POST':
        researcher = request.form['entity_value']
        return redirect(url_for('show_researcher_profile', id=researcher))
    return show_search_form('Researcher', '/researcher')

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
    pass

def show_search_form(entity_name, action):
    return render_template('search_entity.html', entity_name=entity_name, action=action)

@app.route('/fos', methods=['POST', 'GET'])
def find_field():
    if request.method == 'POST':
        fos = request.form['entity_value']
        return redirect(url_for('show_field', field_name=fos))
    return show_search_form('Field Of Study', '/fos')

@app.route('/fos/<field_name>')
def show_field(field_name):
    errors = []
    results = {}
    try:
        # QUERY FOR AUTHORS HAVING THE FOS
        session = Session(engine)
        try:
            res = session.query(Author).filter(Author.fields_of_study.contains(cast([field_name], postgresql.ARRAY(String)))).all()
        finally:
            session.close()
    except Exception as e:
        errors.append(e)
        return render_template('fos.html', errors=errors)

    print('Got {0} results.'.format(len(res)))
    return render_template('fos.html', results=res, field_of_study=field_name)

if __name__ == '__main__':
    print(environ['APP_SETTINGS'])
    app.run()
