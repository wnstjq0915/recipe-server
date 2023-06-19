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

from resources.user import UserRegisterResource, UserLoginResource, UserLogoutResource, jwt_blocklist
from flask_jwt_extended import JWTManager
from config import Config

app = Flask(__name__)

# 환경변수 셋팅
app.config.from_object(Config)

# JWT 메니저 초기화
jwt = JWTManager(app)

# 로그아웃된 토큰으로 요청하는 경우:
# 이 경우는 비정상적인 경우이므로
# jwt가 알아서 처리하도록 코드작성.
@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blocklist

api = Api(app)


# 경로와 API 동작코드(Resource)를 연결한다.
api.add_resource(RecipeListResource, '/recipes') # url 뒤에 붙은 /recipes
api.add_resource(RecipeResource, '/recipes/<int:recipe_id>')
api.add_resource( UserRegisterResource , '/user/register')
api.add_resource( UserLoginResource , '/user/login')
api.add_resource( UserLogoutResource , '/user/logout')

if __name__ == '__main__':
    app.run()