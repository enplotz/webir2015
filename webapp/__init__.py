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

toolbar = DebugToolbarExtension(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    if request.method == 'POST':
        fos = request.form['field_of_study']
        try:
            print(fos)
            # QUERY FOR AUTHORS HAVING THE FOS
            session = Session(engine)
            try:
                res = session.query(Author).filter(Author.fields_of_study.contains(cast([fos], postgresql.ARRAY(String)))).all()
            finally:
                session.close()
        except Exception as e:
            errors.append(e)
            return render_template('index.html', errors=errors)
        if res:
            print('Got {0} results. First is {1}.'.format(len(res), res[0]) )
            return render_template('index.html', results=res, field_of_study=fos)
    return render_template('index.html')


if __name__ == '__main__':
    print(environ['APP_SETTINGS'])
    app.run()
