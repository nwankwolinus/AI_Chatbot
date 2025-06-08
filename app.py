import os
import openai
import requests
import gradio as gr
from datetime import datetime
import pytz

# Load API keys from environment variables (Hugging Face Secrets)
openai.api_key = os.getenv("OPENAI_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
google_cse_id = os.getenv("GOOGLE_CSE_ID")

def needs_live_data(user_input):
    keywords = ['weather', 'news', 'stock', 'price', 'latest', 'current', 'today', 'now']
    return any(word in user_input.lower() for word in keywords)

def google_search(query, api_key, cse_id):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}"
    response = requests.get(url)
    results = response.json()
    if 'items' in results:
        return results['items'][0]['snippet']
    else:
        return "Sorry, no live data found."

def ask_openai(messages, model="gpt-4o-mini"):
    response = openai.chat.completions.create(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content

def chatbot_response(user_input):
    if needs_live_data(user_input):
        live_info = google_search(user_input, google_api_key, google_cse_id)
        prompt = (
            f"The user asked: '{user_input}'. Here is some live information to help answer: {live_info}. "
            "Please provide a helpful and friendly answer based on this information."
        )
    else:
        prompt = f"The user asked: '{user_input}'. Provide a helpful and friendly answer."

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt},
    ]
    return ask_openai(messages)

def chat_interface(user_input, chat_history):
    response = chatbot_response(user_input)
    chat_history = chat_history or []
    chat_history.append(("You", user_input))
    chat_history.append(("AI", response))
    return chat_history, ""

with gr.Blocks() as demo:
    gr.Markdown("# Hybrid AI Chatbot with Live Search")

    chatbot = gr.Chatbot()
    msg = gr.Textbox(show_label=False, placeholder="Type your message here...")
    clear = gr.Button("Clear")
    send = gr.Button(value="Send", elem_id="send-button")

    def respond(user_input, chat_history):
        chat_history, _ = chat_interface(user_input, chat_history)
        return chat_history, ""

    send.click(respond, [msg, chatbot], [chatbot, msg])
    msg.submit(respond, [msg, chatbot], [chatbot, msg])
    clear.click(lambda: None, None, chatbot)

demo.launch()
