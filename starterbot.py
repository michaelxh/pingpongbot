import os
import time
from threading import Thread, Lock
import pickle
from slackclient import SlackClient

#starter bots id
BOT_ID = os.environ.get("BOT_ID")

#constants
AT_BOT = "<@U1NBXQ15Z>:"

API_TOKEN = "xoxb-56405817203-m3uKEp6XWvwXoATDpZjdk0mT"

slack_client = SlackClient(API_TOKEN)
players = {}
standings = {}
players_lock = Lock()
standings_lock = Lock()

def load_players():
    with open(PLAYER_PKL_PATH, 'r') as p:
        players = pickle.load(p)
        return players

def save_players(players):
    with open(PLAYER_PKL_PATH, 'w') as p:
        pickle.dump(players, p)

def load_standings():
    with open(STANDINGS_PKL_PATH, 'r') as s:
        standings = pickle.load(s)
        return standings

def save_standings(standings):
    with open(STADINGS_PKL_PATH, 'w') as s:
        pickle.dump(standings, s)


HELLO_COMMAND = "hey"
EXAMPLE_COMMAND = "do"
REGISTER_COMMAND = "register"

def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."

    if command.startswith(EXAMPLE_COMMAND):
        response = "Sure...write some more code then I can do that!"
    elif command.startswith(HELLO_COMMAND):
        response = "Hey is for horses"
    elif command.startswith(REGISTER_COMMAND):
        new_player = slack_client.api_call("users.info",
                        token=API_TOKEN, user=user)["user"]["name"]
        with players_lock:
            if not new_player in players:
                players[user] = 0
                response = "Registered " + new_player
            else:
                repsonse = new_player + ", you've already been registered"
    print response
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    # print output_list
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output['user']
    return None, None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                t = Thread(target=handle_command, args=(command,channel,user))
                t.start()
                # handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
