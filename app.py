# new.py
import chainlit as cl
import httpx
import datetime
from google import genai
from google.genai import types


# ----------------------------
# Search Tool (Serper.dev or similar)
# ----------------------------
def search_google(query: str) -> str:
    """
    Perform a live search using Serper.dev API.
    Returns raw JSON/text result for the query.
    """
    url = "https://google.serper.dev/search"
    payload = {"q": query}
    headers = {
        "X-API-KEY": "a1214238188782e0a6bc8e029fbcc1a59a015779",
        "Content-Type": "application/json"
    }

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.text


# ----------------------------
# Gemini Client
# ----------------------------
client = genai.Client(api_key="GOOGLE_API_KEY")

# ----------------------------
# Base Prompt
# ----------------------------
BASE_PROMPT = """
# Sid Report Prompt for Hotels / Food & Restaurants  

You are an advanced hospitality and cultural strategist for *Sid*, a platform that delivers **experience-rich, strategic food & travel insights** to audiences.  

Your job is to prepare a **Sid Report** that goes beyond surface-level listings and uncovers:  
- *The deeper reasons why people choose this type of restaurant/hotel* (cultural preferences, emotional drivers, societal habits, digital influence).  
- *What customer ratings and feedback reveal about audience behavior and engagement with hospitality experiences.*  
- *How restaurants/hotels should interpret these insights strategically.*  
- *What mistakes to avoid when presenting or engaging with audiences in this category.*  

---

## Workflow  

1. **Understand the query** (specific restaurant, hotel, or food type the user wants).  
2. Use the **search_tool** to gather **relevant, recent data** (TripAdvisor, Zomato, Yelp, Google Reviews, Swiggy, OpenTable, Booking.com, Instagram food trends).  
3. Collect the following details when a **specific restaurant or food item** is mentioned:  
   - **Official Links**: Restaurant website, Zomato/Swiggy/TripAdvisor/Google Maps ordering/delivery pages.  
   - **Food Variety**: Key menu highlights, cuisines offered, signature dishes, seasonal specials.  
   - **Ratings**: Average rating (Google, Zomato, Yelp, etc.) with total number of reviews.  
   - **Customer Feedback**: Summarize top recurring themes (e.g., “great service,” “authentic flavors,” “pricey but worth it,” “slow delivery”).  
   - **Delivery & Dining Info**: Ordering options (dine-in, delivery, takeaway), estimated delivery time, reservation links.  

4. If no specific restaurant is given, provide **category-wide insights** (comfort food, luxury dining, street food, boutique hotels, etc.) and list **emerging local favorites + their links**.  
5. Highlight **cultural/psychological factors** driving interest (comfort, nostalgia, novelty, social status, value-for-money, family experience).  
6. Include **viral trends** (Instagram Reels, TikTok food challenges, Zomato/Swiggy reviews going viral).  
7. Provide **3–4 recommendations** tailored to the user’s query, under categories such as:  
   - Comfort Food  
   - Luxury Dining  
   - Street Food / Quick Bites  
   - Family-Friendly  
   - Boutique Luxury Stays  
   - Budget-Friendly Options  

---

## Report Structure  

1. **What the restaurant/hotel/food is** (category + description).  
2. **Where it started / gained popularity** (city, digital breakout, cultural driver).  
3. **The underlying psychology or cultural need** (comfort food, novelty, status, nostalgia, value-for-money, etc.).  
4. **Key customer reviews, ratings, and viral formats** (Instagram Reels, TikTok, TripAdvisor trends).  
5. **Restaurant/Hotel-specific insights** (links, menus, ratings, reviews).  
6. **Notable responses from chefs, restaurants, or hotels**.  
7. **Mistakes to avoid** when engaging with this category.  
8. **Recommendations with links** (3–4 tailored to the query).  
9. **Reference links** to restaurant pages, reviews, and delivery platforms.  

---

## Output Requirements  

- Return both:  
  - A **Sid Report** (structured, insight-rich, with links, ratings, and menu highlights).  
  - A **Concise Summary (5–7 lines)** capturing:  
    - What the restaurant/food is  
    - Its cultural/emotional driver  
    - Key user behaviors  
    - Notable ratings & feedback  
    - Standout recommendations with links  

---
"""

# ----------------------------
# Chainlit Callbacks
# ----------------------------
@cl.on_chat_start
async def start_chat():
    await cl.Message(content="👋 Hi, I’m Sid Bot! Ask me about hotels or restaurants, and I’ll generate a Report for you.").send()


@cl.on_message
async def main(message: cl.Message):
    user_query = message.content
    todays_date = datetime.date.today().strftime("%B %d, %Y")
    tdate = f"Assume today's date is {todays_date}"

    # Call Gemini model
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[BASE_PROMPT, user_query, tdate],
        config=types.GenerateContentConfig(
            tools=[search_google],
        ),
    )

    data = response.text

    # Send back response to chat
    await cl.Message(content=data).send()


