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

async def generate_video_ideas(topics):

    prompt = f"""
أنت خبير صناعة محتوى يوتيوب في مجال الأمن السيبراني.

الجمهور:
- مبتدئون
- مهتمون بـ Termux و Linux و Kali Linux
- يحبون معرفة الأدوات والأخبار التقنية

حول هذه المواضيع إلى أفكار فيديوهات:

{topics}


لكل فكرة اكتب:

🎥 عنوان جذاب:
💡 الفكرة:
📚 ماذا سيتعلم المشاهد:
⏱ مدة مناسبة:
🏷 مستوى الصعوبة:

اختر أفكار تعليمية وآمنة.
لا تقدم خطوات اختراق ضارة.
"""


    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }


    body = {
        "model": "llama-3.1-8b-instant",

        "messages": [
            {
                "role": "user",
                "content": prompt
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

        data = response.json()

        return data["choices"][0]["message"]["content"]