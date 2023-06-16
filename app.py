# conda create -n lambda_app python==3.10
# flask 설치
# pip install flask flask-restful

# 실행
# flask run 
# python app.py

from flask import Flask

app = Flask(__name__)

if __name__ == '__main__':
    app.run()