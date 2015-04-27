# -*- coding: utf-8 -*-

from flask import Flask, render_template, request


app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/doc')
def doc():
    return render_template('doc.html')


@app.route('/demo')
def demo():
    return render_template('demo.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)