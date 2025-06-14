from flask import Flask, render_template
from dotenv import load_dotenv
import os



load_dotenv()
app = Flask(__name__, template_folder='../templates')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    return render_template('index.html')
