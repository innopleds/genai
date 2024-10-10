from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import os 
from dotenv import load_dotenv
import pandas as pd
from fastapi import FastAPI, HTTPException

load_dotenv()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pwd = os.getenv('DB_PWD')

url = f'postgresql://{db_user}:{db_pwd}@{db_host}/postgres'
engine = create_engine(url)
Session = sessionmaker(bind=engine)


session = Session()

def get_param_info(result_image_id):
    query = f"""
        SELECT *
        FROM public.parameterinfo
        WHERE image_id = '{result_image_id}';
        """
    
    df = pd.read_sql_query(query, con=engine)
    if df.empty:
        session.close()
        raise HTTPException(status_code=404, detail="Image ID not found in the database.")
    return df

def input_img(result_image_id):
    input_img_query = text("""
        SELECT input_img_url
        FROM public.image
        WHERE id = :result_image_id
        """)
    input_img_result = session.execute(input_img_query, {'result_image_id': result_image_id}).fetchone()
    session.commit()
    
    if input_img_result is None:
        session.close()
        raise HTTPException(status_code=404, detail="Input image not found in the database.")
    return input_img_result

def mask_img(result_image_id):
    mask_img_query = text("""
    SELECT mask_img_url
    FROM public.image
    WHERE id = :result_image_id
    """)
    mask_img_result = session.execute(mask_img_query, {'result_image_id': result_image_id}).fetchone()
    session.commit()

    if mask_img_result is None:
        session.close()
        raise HTTPException(status_code=404, detail="Input image not found in the database.")
    return mask_img_result

def error_msg(err_msg, result_image_id):
    gen_error_msg = text("""
        UPDATE public.image
        SET error = :err_msg, status = 'failed'
        WHERE id = :result_image_id
        """)
    session.execute(gen_error_msg, {'err_msg': err_msg, 'result_image_id': result_image_id})
    session.commit()
    session.close()
    
def gen_completed(image_urls, result_image_id, seed_value):

    current_info_query = text("""
        SELECT info
        FROM public.image
        WHERE id = :result_image_id
    """)
    
    result = session.execute(current_info_query, {'result_image_id': result_image_id}).fetchone()
    if result is None:
        raise HTTPException(status_code=404, detail="Image not found")


    if isinstance(result[0], str):
        info_json = json.loads(result[0])  
    else:
        info_json = result[0]

    info_json['seed'] = seed_value


    updated_info = json.dumps(info_json)

    update_url_query = text("""
        UPDATE public.image
        SET url = :image_url, info = :updated_info, status = 'completed'
        WHERE id = :result_image_id
    """)
    session.execute(update_url_query, {
        'image_url': image_urls,
        'updated_info': updated_info,
        'result_image_id': result_image_id
    })
    session.commit()
    session.close()
    
def gen_processing(result_image_id):
    update_query = text("""
    UPDATE public.image
    SET status = 'processing'
    WHERE id = :result_image_id
    """)

    session.execute(update_query, {'result_image_id': result_image_id})
    session.commit()
    
def db_prompt_en(user_prompt_en, result_image_id):
    update_query = text("""
        UPDATE public.image
        SET prompt_en = :user_prompt_en
        WHERE id = :result_image_id
        """)
    session.execute(update_query, {'user_prompt_en':user_prompt_en, 'result_image_id': result_image_id})
    session.commit()

def db_negative_en(user_prompt_en, result_image_id):
    update_query = text("""
        UPDATE public.image
        SET negative_en = :user_prompt_en
        WHERE id = :result_image_id
        """)
    session.execute(update_query, {'user_prompt_en':user_prompt_en, 'result_image_id': result_image_id})
    session.commit()