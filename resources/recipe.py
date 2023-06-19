from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from flask import request
from mysql_connection import get_connection
from mysql.connector import Error
import mysql.connector

# API 동작하는 코드를 만들기 위해서는
# class(클래스)를 만들어야 한다.

# class 란 비슷한 데이터끼리 모아놓은 것(테이블 생각)
# 클래스는 변수와 함수로 구성된 묶음
# 테이블과 다른점 : 함수가 있다는 점 

# API를 만들기 위해서는, 
# flask_restful 라이브러리의 Resource 클래스를
# 상속해서 만들어야 한다. 파이썬에서 상속은 괄호


class RecipeResource(Resource):
    
    # GET 메소드에서, 경로로 넘어오는 변수는 get 함수의 파라미터로사용

    def get(self, recipe_id):


        # 1. 클라이언트로부터 데이터를 받아온다.
        # 위의 recipe_id 에 담겨있다.
        print(recipe_id)
        print(type(recipe_id))
        
        # 2. 데이터베이스에 레시피 아이디로 쿼리한다.
        try :
            connection = get_connection()

            query = '''
                    select r.*, username
                    from recipe r
                    join user u
                    on r.user_id = u.id
                    where is_publish = 1 and r.id = %s;'''
            record = (recipe_id, )
            cursor =connection.cursor(dictionary=True)  #dictionary=True = json 형식으로가져오게한다
            cursor.execute(query, record)
            result_list = cursor.fetchall()    #fetchall 데이터 있는거 전부 가져와라
            print(result_list)
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            return{'result': 'fail', 'error':str(e)}, 500
        # 3. 데이터가공이 필요하면, 가공한 후에
        #    클라이언트에 응답한다.
        i = 0
        for row in result_list :
            result_list[i]['created_at'] = row['created_at'].isoformat()    
            result_list[i]['updated_at'] = row['updated_at'].isoformat()   
            i = i + 1
        if len(result_list) != 1:
            return{'result' : 'success', 'item' : {}}
        else :
            return{'result' : 'success', 'item' : result_list[0]}
        
        
    
        # 3. 결과를 클라이언트에 응답한다
    @jwt_required()
    def put(self, recipe_id) :
        # 1. 클라이언트로부터 데이터 받아온다.
        print(recipe_id)
        # body 에 있는 json 데이터를 받아온다.
        data = request.get_json()

        # user_id를 받아온다.
        user_id = get_jwt_identity()
        # 2. 데이터베이스에 update 한다.
        try : 
            connection = get_connection()
            query = '''  update recipe
                        set name = %s, description =%s, num_of_servings = %s , cook_time = %s,
                        directions = %s, is_publish = %s
                        where id = %s and user_id = %s;
                    '''
            record = ( data['name'], 
                    data['description'] , 
                    data['num_of_servings'], 
                    data['cook_time'], 
                    data['directions'], 
                    data['is_publish'],
                    recipe_id,
                    user_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            return {'result': 'fail', 'error' : str(e)}, 500
        

        return {'result' : 'success'}
    
    @jwt_required()
    def delete(self, recipe_id):
        # 1. 클라이언트로부터 데이터 받아온다
        print(recipe_id)
        user_id = get_jwt_identity()
        # 2. DB에서 삭제한다
        try:
            connection = get_connection()
            query = ''' delete from recipe
                        where id = %s and user_id = %s;
                    '''
            record = (recipe_id ,user_id)   # 튜플에 하나 넣을때는 , 를 넣어야 튜플 유지됨
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            return{'result' : 'success', 'error' : str(e)}



        # 3. 결과를 응답한다.

        return {'result' : 'success'}
class RecipeListResource(Resource):

    @jwt_required()
    def post(self) :

        # {
        # "name": "김치찌게",
        # "description": "맛있게 끓이는 방법",
        # "num_of_servings": 4,
        # "cook_time": 30,
        # "directions": "고기 볶고 김치 넣고 물 붓고 두부 넣고",
        # "is_publish": 1
        # }



        # 1. 클라이언트가 보낸 데이터를 받아온다.
        data = request.get_json()

        # 1-1. 헤더에 담긴 JWT 토큰 받아온다.
        user_id = get_jwt_identity()

        print(user_id)


        # 2. DB에 저장한다.
        try : 
            # 2-1. 데이터베이스를 연결한다.
            connection = get_connection()
            # 2-2 쿼리문을 만든다
            #### 중요 : 컬럼과 매칭되는 데이터만 %s 로 바꿔준다.

            query = '''insert into recipe
            (name, description, num_of_servings, cook_time, directions, is_publish, user_id)
            values
            (%s, %s, %s,%s , %s, %s, %s);
                        
            '''
            # 2-3. 쿼리에 매칭되는 변수 처리 튜플로 처리해준다. query %s에 들어갈것들 
            record = (data['name'], data['description'], data['num_of_servings'], data['cook_time'], data['directions'], data['is_publish'], user_id)

            # 2-4. 커서를 가져온다.
            cursor = connection.cursor()

            # 2-5. 쿼리문을, 커서로 실행한다.
            cursor.execute(query,record)
            # 2-6. DB에 반영 완료하라는, commit 해줘야한다.
            connection.commit()
            # 2-7.자원해제
            cursor.close()
            connection.close()

    
        except Error as e:
            print(e)
            return {'result' : 'fail', 'error' : str(e)}, 500
        



        # 3. 에러가 났으면, 에러가 났다고 알려주고
        #    그렇지 않으면 잘 저장됐다고 알려준다.



        
        return {'result':'success'}
    
    def get(self) :

        # 1. 클라이언트로 부터 데이터를 받아온다.
        # 2. 저장된 레시피 리스트를 DB로부터 가져온다.
        # 2-1. DB 커넥션

        try :
            connection = get_connection()

            # 2-2. 쿼리문 만든다.

            qeury = '''select r.*, username
                        from recipe r
                        join user u
                        on r.user_id = u.id
                        where is_publish = 1
                        order by created_at desc;'''
            # 2-3 . 변수로 처리할 부분은 변수처리한다.

            # 2-4. 커서 가져온다,
            cursor = connection.cursor(dictionary= True)
            # 2-5. 쿼리문을 커서로 실행한다.
            cursor.execute(qeury)

            # 2-6.실행결과를 가져온다.
            result_list = cursor.fetchall()
            print(result_list)

            cursor.close()
            connection.close()
        
        except Error as e :
            print(e)
            return {'result' : 'fail', 'error' : str(e)}, 500






        # 3. 데이터가공이 필요하면, 가공한 후에
        #    클라이언트에 응답한다.
        i = 0
        for row in result_list :
            result_list[i]['created_at'] = row['created_at'].isoformat()    
            result_list[i]['updated_at'] = row['updated_at'].isoformat()    
            i = i + 1

        return {'result' : 'success', 
                'count' : len(result_list),
                'items' : result_list}