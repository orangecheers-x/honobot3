import requests
import os
key = os.getenv('OPENAI_API_KEY')
# curl https://api.openai.com/v1/completions \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer $OPENAI_API_KEY" \
#   -d '{
#     "model": "text-davinci-003",
#     "prompt": "Say this is a test",
#     "max_tokens": 7,
#     "temperature": 0
#   }'
print(key)
res = requests.post('https://api.openai.com/v1/chat/completions',
                    headers={'Authorization': f'Bearer {key}'},
                    json={
                        "max_tokens": 500,
                        "messages": [{"role": "user", "content": "你是河南人"}],
                        "model": "gpt-3.5-turbo"
                    },
                    proxies={'http': 'http://192.168.1.24:7891',
                             'https': 'http://192.168.1.24:7891'}

                    ).json()

print(res)
