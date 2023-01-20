import requests


def get_update_message(config):
    recipient_id = config['recipient_id']
    bot_token = config['token']

    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    response = requests.get(url).json()
    print(response)
    if response and response['ok']:
        for update in response['result']:
            update_id = update['update_id']
            print(update_id)
            url = f"https://api.telegram.org/bot{bot_token}/Update/update_id={update_id}"
            response = requests.get(url).json()
            print(response['ok'])
    return False


def send_message(config, message):
    chat_id = config['recipient_id']
    bot_token = config['token']

    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"

    response = requests.get(url).json()
    print(response)
    if response and response['ok']:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(url).json()
        print(response)
        if response:
            return True
    return False


def get_chat(config, chart_name):
    bot_token = config['token']
    url = f"https://api.telegram.org/bot{bot_token}/getChat?chat_id={chart_name}"
    response = requests.get(url).json()
    print(response)


def send_message_users(config, message):
    recipients = config['recipient_ids']
    bot_token = config['token']
    for chat_id in recipients:
        if chat_id.startswith('@'):
            get_chat(config, chat_id)
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
        response = requests.get(url).json()
        print(response)


def send_message_to_all(config, message):
    try:
        bot_token = config['token']
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url).json()
        chats = set()
        if response and response['ok']:
            for update in response['result']:
                chat_id = update['message']['chat']['id']
                chats.add(chat_id)
            for chat_id in chats:
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={message}"
                requests.get(url).json()
            return True
        return False
    except Exception:
        return False


if __name__ == "__main__":
    config = {
        'token': '',
    }
    send_message_to_all(config, "test\ntest")
