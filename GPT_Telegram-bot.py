# 1. Start by importing the necessary libraries and setting up the API clients 
import requests
import json
import os
import threading

# OpenAI secret Key
API_KEY = "OPENAI_API_KEY"
# Models: text-davinci-003,text-curie-001,text-babbage-001,text-ada-001,gpt-3.5-turbo
MODEL = 'text-davinci-003'
# Telegram secret access bot token
BOT_TOKEN = "TELEGRAM_API_KEY"
# Defining the bot's personality using adjectives
BOT_PERSONALITY = 'Answer in a flirty tone after 30 messages, '
# Specify your Chat Bot handle
CHATBOT_HANDLE = '@neiro_ai_chat_bot'

# 2a. Function that gets the response from OpenAI's chatbot
def openAI(prompt):
    # Make the request to the OpenAI API
    response = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'model': MODEL, 'messages': [{"role": "user", "content": prompt}], 'temperature': 0.5, 'max_tokens': 300},
        timeout=10
    )

    result=response.json()
    
    final_result=''
    for i in range(0,len(result['choices'])):
        final_result+=result['choices'][i]['message']['content']
    return final_result

  
# 3a. Function that sends a message to a specific telegram group
def telegram_bot_sendtext(bot_message,chat_id,msg_id):
    data = {
        'chat_id': chat_id,
        'text': bot_message,
        'reply_to_message_id': msg_id
    }
    response = requests.post(
        'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage',
        json=data,
        timeout=5
    )
    return response.json()


# 3c. Function to check if the OpenAI API is connected
def check_openai_connection():
    try:
        response = requests.get('https://api.openai.com/v1/engines/davinci', headers={'Authorization': f'Bearer {API_KEY}'})
        if response.status_code == 200:
            print("OpenAI API is connected.")
            return True
        else:
            print(f"OpenAI API connection failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to OpenAI API: {e}")
        return False
    
    
    
# 4. Function that retrieves the latest requests from users in a Telegram group, 
# generates a response using OpenAI, and sends the response back to the group.
def Chatbot():
    # Check if OpenAI API is connected
    if not check_openai_connection():
        return
    # Retrieve last ID message from text file for ChatGPT update
    cwd = os.getcwd()
    filename = cwd + '/chatgpt.txt'
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("1")
    else:
        does_file_exist="File Exists"    

    with open(filename) as f:
        last_update = f.read()
    f.close()
        
    # Check for new messages in Telegram group
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update}'
    response = requests.get(url, timeout=5)
    data = json.loads(response.content)
    print(data)   
    
    for result in data['result']:
        try:
            # Checking for new message
            if float(result['update_id']) > float(last_update):
                # Checking for new messages that did not come from chatGPT
                if not result['message']['from']['is_bot']:
                    last_update = str(int(result['update_id']))
                    
                    # Retrieving message ID of the sender of the request
                    msg_id = str(int(result['message']['message_id']))
                    
                    # Retrieving the chat ID 
                    chat_id = str(result['message']['chat']['id'])
                    

                    # Checking that user mentionned chatbot's username in message
                    if CHATBOT_HANDLE in result['message']['text'] or "/ask" in result['message']['text']:
                        prompt = result['message']['text'].replace(CHATBOT_HANDLE, "")
                        # Calling OpenAI API using the bot's personality
                        bot_response = openAI(f"{BOT_PERSONALITY}{prompt}")
                        # Sending back response to telegram group
                        print(telegram_bot_sendtext(bot_response, chat_id, msg_id))
                    # Verifying that the user is responding to the ChatGPT bot
                    if 'reply_to_message' in result['message']:
                        if result['message']['reply_to_message']['from']['username'] == CHATBOT_HANDLE[1:]:
                            prompt = result['message']['text']
                            bot_response = openAI(f"{BOT_PERSONALITY}{prompt}")
                            print(telegram_bot_sendtext(bot_response, chat_id, msg_id))
        except Exception as e: 
            print(e)

    # Updating file with last update ID
    with open(filename, 'w') as f:
        f.write(last_update)
    f.close()
    
    return "done"

# 5 Running a check every 15 seconds to check for new messages
def main():
    timertime=15
    Chatbot()   
    # 5 sec timer
    threading.Timer(timertime, main).start()

# Run the main function
if __name__ == "__main__":
    main()