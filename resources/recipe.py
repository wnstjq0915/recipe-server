from flask_restful import Resource
from flask import request
from mysql.connector import Error
# pip install mysql-connector-python
import mysql.connector
from mysql_connection import get_connection
# API 동작하는 코드를 만들기 위해서는
# class(클래스)를 만들어야 한다.


# class란? 비슷한 데이터끼리 모아놓은 것 (테이블 생각)
# 클래스는 변수와 함수로 구성된 묶음
# 테이블과 다른점: 함수가 있다는 점!

# API를 만들기 위해서는
# flask_restful 라이브러리의 Resource 클래스를
# 상속해서 만들어야 한다. 파이썬에서 상속은 괄호!

# GET 메소드에서 경로로 넘어오는 변수는 get 함수의 파라미터로 사용
class RecipeResource(Resource):
    def get(self, recipe_id):
        # 1. 클라이언트로부터 데이터를 받아온다.
        # 위의 recipe_id에 담겨있다.
        


        # 2. 데이터베이스에 레시피 아이디로 쿼리한다.
        try:
            connection = get_connection()
            query = '''select *
                    from recipe
                    where id = %s;'''
            record = (recipe_id, )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            print(result_list)


        except Error as e:
            print(e)
            return {'result': 'fail', 'error': str(e)}, 500


        # 3. 데이터가공이 필요하면 가공한 후에
        # 클라이언트에 응답한다.
        i = 0
        for row in result_list:
            print(type(result_list[i]['created_at']))
            result_list[i]['created_at'] = row['created_at'].isoformat()
            result_list[i]['updated_at'] = row['updated_at'].isoformat()
            i += 1
        if len(result_list) != 1:
            return {'result': 'success', 'item': {}}
        else:
            return {'result': 'success', 'item': result_list[0]}
        
            # 클래스를 하나 더 안 만들고 함수의 default값을 정해서 get할 때.
            # return {'result': 'success', 'item': [i for i in result_list if i['id'] == recipe_id][0]}

    def put(self, recipe_id):
        
        # 1. 클라이언트로부터 데이터를 받아온다.
        print(recipe_id)

        # body에 있는 json 데이터를 받아온다.
        data = request.get_json()
        # 2. 데이터베이스에 update 한다.
        try:
            connection = get_connection()
            query = '''update recipe
                    set name = %s, description = %s,
                        num_of_servings = %s, cook_time = %s,
                        directions = %s, is_publish = %s
                    where id = %s;'''
            record = (data['name'], data['description'], data['num_of_servings'],
                    data['cook_time'], data['directions'], data['is_publish'], recipe_id)
            
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result': 'fail', 'error': str(e)}, 500

        return {'result': 'success'}

    def delete(self, recipe_id):
        # 1. 클라이언트로부터 데이터를 받아온다.
        print(recipe_id)

        # 2. DB에서 삭제한다.
        try:
            connection = get_connection()
            query = '''delete from recipe
                    where id = %s;'''
            record = (recipe_id, )

            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            cursor.close()
            connection.close()
        except Error as e:
            print(e)
            return {'result': 'fail', 'error': str(e)}
        # 3. 결과를 응답한다.
        return {'result': 'success'}

class RecipeListResource(Resource):
    def post(self):
        # 포스트로 요청한 것을 처리하는 코드 작성을 우리가
        # print('API 동작')


        # {
        #     "name": "김치찌개",
        #     "description": "김치찌개 맛있게 끓이는 방법",
        #     "num_of_servings": 4,
        #     "cook_time": 30,
        #     "directions": "고기볶고 김치넣고 물 붓고 두부넣고",
        #     "is_publish": 1
        # }


        # 1. 클라이언트가 보낸 데이터를 받아온다.
        data = request.get_json()
        print(data)


        # 2. DB에 저장한다.
        try:
            # 2-1. 데이터베이스를 연결한다.
            connection = get_connection()

            # 2-2. 쿼리문 만든다
            ### 중요! 컬럼과 매칭되는 데이터만 %s로 바꿔준다.
            query = '''insert into recipe
                    (name, description, num_of_servings, cook_time,
                        directions, is_publish)
                    values
                    (%s, %s, %s, %s, %s, %s);'''
            # 쿼리문 워크플레이스에서 확인하고 테스트 해본 뒤에 넣기.

            # 2-3. 쿼리에 매칭되는 변수 처리! 중요! 튜플로 처리해준다!
            record = (data['name'],
                    data['description'],
                    data['num_of_servings'],
                    data['cook_time'],
                    data['directions'],
                    data['is_publish'])
            
            # 2-4. 커서를 가져온다.
            cursor = connection.cursor()

            # 2-5. 쿼리문을 커서로 실행한다.
            cursor.execute(query, record)

            # 2-6. DB에 반영 완료하라는 commit해줘야 한다.
            connection.commit()

            # 2-7. 자원해제
            cursor.close()
            connection.close()
        except Error as e:
            print(e)
            return {'result': 'fail', 'error': str(e)}, 500 # http상태 500은 서버에러. 임의로 상태코드 설정.


        # 3. 에러가 났으면, 에러가 났다고 알려주고
        # 그렇지 않으면 잘 저장되었다고 알려준다.

        return {"result":'success'} # 파이썬이라 큰따옴표 안해도 됨.
    # 포스트맨 워크스페이스에서 POST하면 MYSQL에서 확인했을 때 recipe_db 속 recipe 테이블에 들어감.

    def get(self):
        # 코드 작성
        # print("레시피 가져오는 API 동작했음.")

        # 1. 클라이언트로부터 데이터를 받아온다.

        # 2. 저장된 레시피 리스트를 DB로부터 가져온다.
        try:
            # 2-1. DB 커넥션
            connection = get_connection()

            # 2-2. 쿼리문 만든다.
            query = '''select * from recipe
                    order by created_at desc;'''

            # 2-2. 변수처리할 부분은 변수처리한다.

            # 2-3. 커서 가져온다.
            cursor = connection.cursor(dictionary=True)

            # 2-4. 쿼리문을 커서로 실행한다.
            cursor.execute(query)

            # 2-5. 실행결과를 가져온다.
            result_list = cursor.fetchall()
            # print(result_list)

            cursor.close()
            connection.close()

        except Error as e:
            print(e)
            return {'result': 'fail', 'error': str(e)}, 500
        # JSON은 파이썬의 datetime을 인식 못 함.

        # 3. 데이터 가공이 필요하면 가공한 후에
        # 클라이언트에 응답한다.

        i = 0
        for row in result_list:
            result_list[i]['created_at'] = row['created_at'].isoformat()
            result_list[i]['updated_at'] = row['updated_at'].isoformat()
            i += 1

        # datetime타입 검사해서 다 바꿔주는거
        # import datetime
        # for row in result_list:
        #     for i in row.items():
        #         if isinstance(i[1], datetime.datetime):
        #             result_list[result_list.index(row)][i[0]] = i[1].isoformat()
        

        return {
            'result': 'success',
            'count': len(result_list),
            'items':result_list
        } # , 200 