from flask import Flask
from dotenv import load_dotenv
import os
from flask import render_template


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

@app.route('/')
def start():
    return render_template('page_analyzer/index.html')
