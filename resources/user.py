# pip install psycopg2-binary
# pip install passlib
# pip install email-validator
# pip install flask-jwt-extended

from flask_restful import Resource
from flask import request
from mysql_connection import get_connection
from mysql.connector import Error
import mysql.connector
from email_validator import validate_email, EmailNotValidError

from utils import hash_password, check_password
from flask_jwt_extended import create_access_token, get_jwt, jwt_required

import datetime

# EmailNotValidError 이메일이 정상이냐


# 클래스는 변수와 함수의 묶음

class UserRegisterResource(Resource):
    def post(self) :
        # {"username" : "홍길동",
        # "email" : "abc@naver.com",
        # "password" : "1234"}
        
        # 1. 클라이언트가 보낸 데이터를 받아준다.

        data = request.get_json()

        # 2. 이메일 주소형식이 올바른지 확인한다.
        try :
            validate_email(data['email'])
        
        


        except EmailNotValidError as e :
            print(e)
            return {'result' : 'fail', 'error' : str(e)} , 400
        
        # 3. 비밀번호 길이가 유효한지 체크
        #    만약, 비번이 4자리 이상 , 12자리 이하라고 한다면,
        if len(data['password']) < 4 or len(data['password']) > 12 :
            return {'result' : 'fail' , 'error' : '비번 길이 에러'}, 400
        
        # 4. 비밀번호를 암호화 한다.
        hashed_password = hash_password(data['password'])
        print(str(hashed_password))

        # 5. DB에 이미 회원 정보가 있는지 확인한다.
        try :
            connection =get_connection()
            query = '''select *
                    from user
                    where email =%s;'''
            record = (data['email'], )

            cursor = connection.cursor()
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            print(result_list)

            if len(result_list) == 1:
                return {'result' : 'fail' , 'error' : '이미 회원가입 한 사람'}, 400
            
            # 회원이 아니므로, 회원가입 코드를 작성한다.
            # DB에 저장한다.
            query = '''insert into user
                    (username, email, password)
                    values
                    (%s, %s, %s);'''
            record = (data['username'], data['email'], hashed_password)
            cursor = connection.cursor()
            cursor.execute(query, record)

            connection.commit()

            # DB에 데이터를 insert한 후에,
            # 그 인서트된 행의 아이디를 가져오는 코드
            user_id = cursor.lastrowid

            cursor.close()
            connection.close()


        except Error as e :
            print(e)
            return {'result' : 'fail' , 'error' : str(e)}, 500

        # create_access_token(user_id, expires_delta=datetime.timedelta(days=10)) # 10분 로그인 유지
        access_token = create_access_token(user_id)

        return {'result' : 'success', 'access_token' : access_token}


# 로그인 관련 개발
class UserLoginResource(Resource):
    def post(self):
        # 1. 클라이언트로부터 데이터 받아온다.
        data = request.get_json()

        # 2. 이메일 주소로, DB에 select 한다.
        try:
            connection = get_connection()
            query = '''select *
                    from user
                    where email = %s;'''
            record = (data['email'], )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()

        except Error as e:
            print(e)
            return {'result' : 'fail', 'error' : str(e)}, 500

        if len(result_list) == 0:
            return {'result' : 'fail', 'error' : '회원가입한 사람 아님'}, 400


        # 3. 비밀번호가 일치하는지 확인한다.
        # 암호화된 비밀번호가 일치하는지 확인해야 함.
        print(result_list)

        check = check_password(data['password'], result_list[0]['password'])
        if check == False:
            return {'result' : 'fail', 'error' : '비번 틀렸음'}, 400


        # 4. 클라이언트에게 데이터를 보내준다.
        # 로그인이 되면 유저id를 암호화해서 이용해야 함.

        access_token = create_access_token(result_list[0]['id'])

        return {'result' : 'success', 'access_token' : access_token} # 실행할 때마다 토큰이 새로 바뀜.

# 로그아웃
# 로그아웃된 토큰을 저장할 set을 만든다.

jwt_blocklist = set()

class UserLogoutResource(Resource):

    @jwt_required()
    def delete(self):
        jti = get_jwt()['jti']
        print(jti)
        jwt_blocklist.add(jti)
        return {'result' : 'success'}


# Bearer    # 이 뒤에 띄어쓰기 한칸 + " 빼고 토큰 붙이기.
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY4NzE1MzUyMSwianRpIjoiM2U0NmI1MWEtMzBmNy00MWM5LWJhZjgtZmJiYTAwYmNkYzA5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MiwibmJmIjoxNjg3MTUzNTIxfQ.akZllLDdGGGO0wbS7zfa5SrbLspvzoVyj_JwGnB6XY8