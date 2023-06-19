# conda create -n lambda_app python==3.10
# flask 설치
# pip install flask flask-restful

# 실행
# flask run 
# python app.py
# 저장하고 하는거 주의

from flask import Flask
from flask_restful import Api
from resources.recipe import RecipeListResource, RecipeResource

from resources.user import UserRegisterResource, UserLoginResource

app = Flask(__name__)
api = Api(app)


# 경로와 API 동작코드(Resource)를 연결한다.
api.add_resource(RecipeListResource, '/recipes') # url 뒤에 붙은 /recipes
api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
api.add_resource( UserRegisterResource , '/user/register')
api.add_resource( UserLoginResource , '/user/login')

if __name__ == '__main__':
    app.run()