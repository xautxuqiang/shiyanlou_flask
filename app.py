# coding: utf-8

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
#mysql_db
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/news'
db = SQLAlchemy(app)
#mongo_db
client = MongoClient('127.0.0.1', 27017)
mongo_db = client.news

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    created_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('posts',lazy=True))

    def add_tag(self, tag_name):
        tag = {"id":self.id, "tname":tag_name}
        tag_in_tags = mongo_db.tags.find_one(tag) 
        if tag_in_tags:
            print("tag_name already in tags!")
        else:
            mongo_db.tags.insert_one(tag)

    def remove_tag(self, tag_name):
        tag = {"id":self.id, "tname":tag_name}
        mongo_db.delete_one(tag)

    @property
    def tags(self):
        result = []
        for tag in mongo_db.tags.find({'id':self.id}):
            result.append(tag['tname'])
        return result

    def __repr__(self):
        return '<File:%r>' % self.title

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return '<Category:%r>' % self.name

@app.route('/')
def index():
    files = File.query.all()
    tags = {}
    for the_file in files:
        tags[the_file.id] = the_file.tags
    return render_template('index.html', files=files, tags=tags)

@app.route('/files/<file_id>')
def file(file_id):
    the_file = File.query.get(file_id)
    if the_file:
        return render_template('file.html', the_file=the_file)
    else:
        return render_template('404.html'), 404

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
