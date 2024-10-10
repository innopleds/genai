import requests
import logging
import json
# import openai
import os
from dotenv import load_dotenv
from pathlib import Path
import psutil
import GPUtil

load_dotenv()
DEEPL_API = os.getenv('DEEPL_API')

# def deepl_translate(text, source_language="KO", target_language="EN"):

#     url_for_deepl = 'https://api-free.deepl.com/v2/translate'
#     params = {'auth_key' : DEEPL_API, 
#               'text' : text, 
#               'source_lang' : source_language, 
#               "target_lang": target_language}

#     result = requests.post(url_for_deepl, data=params, verify=True)
#     translated = result.json()['translations'][0]["text"]
    
#     return translated


async def deepl_translate(text, source_language="KO", target_language="EN"):
    
    url_for_deepl = 'https://api-free.deepl.com/v2/translate'
    params = {
        'auth_key': DEEPL_API,
        'text': text,
        'source_lang': source_language,
        'target_lang': target_language
    }
    # HTTP 오류 발생 예외 처리
    try: 
        result = requests.post(url_for_deepl, data=params, verify=True)
        result.raise_for_status()  
        
        translated = result.json().get('translations', [])[0].get("text", "")
        
        if not translated:
            logging.error(f"No translation found in response. Response: {result.json()}")
            return ""
        
        return translated
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return "Translation request failed."
    
    except (KeyError, IndexError) as e:
        logging.error(f"Parsing response failed: {e}")
        return "Translation response failed."

# OPENAI_KEY = os.getenv('OPENAI_KEY')
# openai.api_key = OPENAI_KEY

# def gpt_translate(text, source_language = 'ko', target_language = 'en'):
#     # 프롬프트 생성
#     prompt = f"Translate the following text from {source_language} to {target_language}:\n\n{text}"

#     # OpenAI API 호출
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",  # GPT-3.5 Turbo 모델을 사용
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant that translates text."},
#             {"role": "user", "content": prompt}
#         ]
#     )

#     # 번역된 텍스트 추출
#     translated_text = response.choices[0].message['content'].strip()
    
#     return translated_text


# def gen_keyword(x):
       
#     gpt_prompt = [
#         {
#             "role": "system",
#             "content": ("You're an artificial intelligence chatbot with a lot of imagination."
#                         "Look at the words you're presented with and imagine what you look like and describe them in detail.\n\n"
#                         "Example:\n"
#                         "Input: 귀여운 아기 공룡\n"
#                         "Output: baby dinosaur, adorable, pink, spotted, short neck, four legs, two small wings")
#         },
#         {
#             "role": "user",
#             "content": ("Imagine the word below and describe their appearance in English in about 20 words, "
#                         f"using mainly nouns and adjectives, separated by commas:\n\n{x}")
#         }
#     ]
    
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=gpt_prompt
#     )
    
#     return response.choices[0].message['content']
async def mem_usage():
    p = psutil.Process()
    #byte를 사람이 인지하기 쉬운 megabyte로 변환
    #megabyte이므로 1024 * 1024의 값을 나눠줌
    print(f'mem usage : {p.memory_info().rss/2**20}MB')
    
    
async def print_gpu_memory():
    gpus = GPUtil.getGPUs()
    for gpu in gpus:
        print(f"GPU ID: {gpu.id}, Memory Free: {gpu.memoryFree}MB, Memory Used: {gpu.memoryUsed}MB, Memory Total: {gpu.memoryTotal}MB")

# GPU 메모리 사용량을 반환하는 함수
async def get_gpu_memory():
    gpus = GPUtil.getGPUs()
    memory_used = sum([gpu.memoryUsed for gpu in gpus])
    return memory_used