import httpx
from config import AI_API_KEY


async def rewrite_news(news):

    prompt = f"""
أنت كاتب محتوى تقني لقناة تيليجرام عربية.

الجمهور:
هواة الأمن السيبراني والاختراق لكن ليس لديهم خبرة عميقة.

حول الخبر التالي إلى منشور ممتع وبسيط:

العنوان:
{news['title']}

الوصف:
{news['summary']}

الشروط:
- ابدأ بعنوان جذاب
- اشرح ماذا حدث
- لماذا يهم المهتمين بالأمن السيبراني
- لا تستخدم مصطلحات معقدة بدون شرح
- اجعل المنشور أقل من 500 كلمة

"""


    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }


    body = {

        "model":"llama-3.1-8b-instant",

        "messages":[
            {
                "role":"user",
                "content":prompt
            }
        ]

    }


    async with httpx.AsyncClient() as client:

        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=body
        )


        response.raise_for_status()

        data=response.json()

        return data["choices"][0]["message"]["content"]