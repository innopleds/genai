import requests
import logging
import json
# import openai
import os
from dotenv import load_dotenv


load_dotenv()
DEEPL_API = os.getenv('DEEPL_API')

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
            print(f"Warning :No translation found in response. Response: {result.json()}")
            return ""
        
        return translated
    
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return "Translation request failed."
    
    except (KeyError, IndexError) as e:
        logging.error(f"Parsing response failed: {e}")
        return "Translation response failed."


async def getAnswer(query):
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    url = "https://api.openai.com/v1/chat/completions"
    model = "gpt-4o"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                      "type": "text",
                      "text": query
                    },
                    {
                      "type": "image_url",
                      "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                      }
                    }
                  ]
            }
        ],
        "temperature": 0.4 
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.textv

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
