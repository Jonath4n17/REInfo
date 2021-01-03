import random, string
from flask import Flask, render_template, url_for, request, redirect, flash, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import urllib.request
import os
from datetime import datetime
from ocr import ocr
from googleSheets import createSheet
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "static/googleKey.json"

app = Flask( 
	__name__,
	template_folder='templates',
	static_folder='static'
)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif']
app.config['UPLOAD_PATH'] = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///receipts.db'
db = SQLAlchemy(app)

class FileContents(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(300))
  path = db.Column(db.String(300))
  content = db.Column(db.Text)
  date_created = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/menu', methods=['POST', 'GET'])
def menu():
  if request.method == 'POST':
    uploaded_file = request.files['img']
    filename = uploaded_file.filename
    if filename != '':
      file_ext = os.path.splitext(filename)[1]
      if (file_ext not in app.config['UPLOAD_EXTENSIONS']):
        abort(400)
      uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

    path = "static/uploads/" + str(filename)
    try:
      content = ocr(path)
      content = json.dumps(content)

      newFile = FileContents(name=filename, path=path, content=content)
      db.session.add(newFile)
      db.session.commit()
    
      data = FileContents.query.order_by(FileContents.date_created).all()
      return render_template('menu.html', data=data)
    except:
      return '<h1>There was a problem processing the receipt, make sure you uploaded the correct file</h1>'
  else:
    data = FileContents.query.order_by(FileContents.date_created).all()
    return render_template('menu.html', data=data)

content = ""

@app.route("/split")
def split():
  prices = []
  for key in content:
    prices.append(content[key])
  return render_template('split.html', content=content, prices=prices)

@app.route("/create")
def create():
  try:
    createSheet(content)
    return render_template('sheets.html')
  except:
    return '<h1>There was a problem creating the Google Sheet</h1>'

@app.route("/view/<int:id>")
def view(id):
  data_to_view = FileContents.query.get_or_404(id)
  path = data_to_view.path
  path = path[7:]
  global content
  content = data_to_view.content
  content = json.loads(content)

  return render_template('content.html', path=path, content=content)

@app.route("/delete/<int:id>")
def delete(id):
  data_to_delete = FileContents.query.get_or_404(id)

  try:
    db.session.delete(data_to_delete)
    db.session.commit()
    return redirect(url_for('menu'))
  except:
    return '<h1>There was a problem deleting that data</h1>'

if __name__ == "__main__": 
  db.create_all()
  app.run()

