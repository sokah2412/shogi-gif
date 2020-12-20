import os
import flask
from werkzeug.utils import secure_filename
import sys
from kg_converter import generate_gif
import uuid

UPLOAD_FOLDER = 'webapp/gif'
ALLOWED_EXTENSIONS = {'kifu', 'kif'}

app = flask.Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = "d477aeffb9f343d5c1a7f62c0dfb5b8aa0c4fc36501615ce"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if flask.request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in flask.request.files:
            return flask.redirect(flask.request.url)
        file = flask.request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return flask.redirect(flask.request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], str(uuid.uuid4()) + '.kifu')
            file.save(file_path)
            gif_name = generate_gif(file_path)
            return flask.redirect(flask.url_for('get_gif', filename=gif_name))
    return flask.render_template("index.html")

@app.route('/get_gif/<filename>')
def get_gif(filename):
    return flask.send_from_directory('gif', filename)
