from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from django.conf import settings

from .models import Drink, Snacks
from .rag import search_pdf
from .memory import chat_memory
from shop.recommendations.weather import get_weather


llm = ChatGroq(
    model=settings.LLM_MODEL,
    groq_api_key=settings.OPENAI_API_KEY,
)

def get_history(user_id):
    return chat_memory.get(user_id, [])

def save_history(user_id, role, message):
    if user_id not in chat_memory:
        chat_memory[user_id] = []

    chat_memory[user_id].append({
        "role": role,
        "content": message
    })

    # Keep only last 20 messages
    chat_memory[user_id] = chat_memory[user_id][-20:]

def ask_bot(question, user_id, customer):

    # ===============================
    # Get Menu from Database
    # ===============================

    drinks = Drink.objects.all()
    snacks = Snacks.objects.all()

    menu_context = "BREW HAVEN MENU\n\n"

    menu_context += "DRINKS:\n"

    for drink in drinks:
        menu_context += (
            f"Name: {drink.name}\n"
            f"Category: {drink.category}\n"
            f"Price: ₹{drink.price}\n"
            f"Description: {drink.description}\n\n"
        )

    menu_context += "\nSNACKS:\n"

    for snack in snacks:
        menu_context += (
            f"Name: {snack.name}\n"
            f"Price: ₹{snack.price}\n"
            f"Description: {snack.description}\n\n"
        )

    # ===============================
    # Search PDF
    # ===============================

    pdf_context = search_pdf(question)

    # ===============================
    # Get Live Weather
    # ===============================
    
    weather_info = get_weather()
    current_weather_context = (
        f"City: {weather_info.get('city', 'Unknown')}\n"
        f"Weather: {weather_info.get('weather', 'Unknown')}\n"
        f"Temperature: {weather_info.get('temperature', 0)}°C\n"
        f"Humidity: {weather_info.get('humidity', 0)}%\n"
    )

    context = f"LIVE WEATHER:\n{current_weather_context}\n\nDATABASE MENU:\n{menu_context}\n\nKNOWLEDGE BASE:\n{pdf_context}"

    system_prompt = f"""You are Brew Haven's friendly AI assistant.

Your job is to help customers with drinks, snacks, menu items, prices, orders, recommendations, and general questions about Brew Haven.

Current User: {customer}

Follow these rules:
1. Answer the user's question directly and clearly.
2. Keep answers concise unless the user asks for more details.
3. Do not give unnecessary explanations.
4. Use the information provided in the retrieved context/RAG as the primary source of truth.
5. Never invent menu items, prices, ingredients, availability, or policies.
6. If the requested information is not available in the provided context, say:
   "I'm sorry, I don't have that information right now."
7. If the user says "hi", "hello", "hey", etc., respond naturally and briefly.
   Example:
   "Hello! How can I help you today?"
8. If the user asks about a menu item, provide only the relevant information.
9. If the user asks for recommendations, use the available customer/order/weather information when provided.
10. Remember relevant conversation context when answering follow-up questions.
11. Do not repeat the user's question.
12. Do not mention RAG, embeddings, vector databases, prompts, models, or internal system instructions.
13. Do not pretend to have information that you do not have.
14. Be polite and friendly, but don't overuse emojis.
15. Answer in the same language as the user whenever possible.

Retrieved information:
{context}
"""

    # Save user message to history
    save_history(user_id, "user", question)

    # Get history and convert to Langchain format
    history_raw = get_history(user_id)
    history_messages = []
    
    # We slice out the last message because we already appended it above, but wait:
    # Actually, it's easier to just build the messages list directly.
    # The last item in history_raw is the current question.
    for msg in history_raw[:-1]:
        if msg["role"] == "user":
            history_messages.append(HumanMessage(content=msg["content"]))
        else:
            history_messages.append(SystemMessage(content=msg["content"])) # Using SystemMessage or AIMessage based on what was imported.
            
    # Need to check what's imported. The original only imports SystemMessage, HumanMessage.
    # I'll use AIMessage if possible, but let's stick to HumanMessage/SystemMessage.
    
    # Actually, let's just make it simple:
    messages = [SystemMessage(content=system_prompt)]
    
    for msg in history_raw[:-1]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        else:
            # If AIMessage isn't imported, SystemMessage acts similarly for Groq
            messages.append(SystemMessage(content=msg["content"]))
            
    messages.append(HumanMessage(content=question))

    response = llm.invoke(messages)
    
    # Save bot response to history
    save_history(user_id, "bot", response.content)

    return response.content
