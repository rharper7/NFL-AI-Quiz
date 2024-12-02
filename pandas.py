import html
from quart import Quart, request, render_template_string
from openai import OpenAI
import json
from dotenv import load_dotenv
import pandas as pd
load_dotenv()
client = OpenAI()
import time

import logging

# Set up logging to display errors
logging.basicConfig(level=logging.DEBUG)

# Initialize Quart app
app = Quart(__name__)
# HTML template for the page
html_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT Response</title>
    <style>
    html, body {
font-family: sans-serif;
font-size:1.2em;
margin: 0;
}
form {
max-width: 480px;
margin: 0 auto;
padding: 16px;
border: 1px solid black;
}
h2 {
text-align: center;
}
pre {
    white-space: pre-wrap;
    word-break: break-all;
    margin: 0 120px;
    border: 1px solid black;
    }
    body {
	margin: 0;
	padding: 0;
}

.container {
	width: 200px;
	height: 100px;
	padding-top: 100px;
	margin: 0 auto;
}

.ball {
	width: 10px;
	height: 10px;
	margin: 10px auto;
	border-radius: 50px;
}

.ball:nth-child(1) {
	background: #ffffff;
	-webkit-animation: right 1s infinite ease-in-out;
	-moz-animation: right 1s infinite ease-in-out;
	animation: right 1s infinite ease-in-out;
}

.ball:nth-child(2) {
	background: #ffffff;
	-webkit-animation: left 1.1s infinite ease-in-out;
	-moz-animation: left 1.1s infinite ease-in-out;
	animation: left 1.1s infinite ease-in-out;
}

.ball:nth-child(3) {
	background: #ffffff;
	-webkit-animation: right 1.05s infinite ease-in-out;
	-moz-animation: right 1.05s infinite ease-in-out;
	animation: right 1.05s infinite ease-in-out;
}

.ball:nth-child(4) {
	background: #ffffff;
	-webkit-animation: left 1.15s infinite ease-in-out;
	-moz-animation: left 1.15s infinite ease-in-out;
	animation: left 1.15s infinite ease-in-out;
}

.ball:nth-child(5) {
	background: #ffffff;
	-webkit-animation: right 1.1s infinite ease-in-out;
	-moz-animation: right 1.1s infinite ease-in-out;
	animation: right 1.1s infinite ease-in-out;
}

.ball:nth-child(6) {
	background: #ffffff;
	-webkit-animation: left 1.05s infinite ease-in-out;
	-moz-animation: left 1.05s infinite ease-in-out;
	animation: left 1.05s infinite ease-in-out;
}

.ball:nth-child(7) {
	background: #ffffff;
	-webkit-animation: right 1s infinite ease-in-out;
	-moz-animation: right 1s infinite ease-in-out;
	animation: right 1s infinite ease-in-out;
}

.ball {
	display: none;
}

.ball {
display: {{switcher}};
}
@-webkit-keyframes right {
	0% {
		-webkit-transform: translate(-15px);
	}
	50% {
		-webkit-transform: translate(15px);
	}
	100% {
		-webkit-transform: translate(-15px);
	}
}

@-webkit-keyframes left {
	0% {
		-webkit-transform: translate(15px);
	}
	50% {
		-webkit-transform: translate(-15px);
	}
	100% {
		-webkit-transform: translate(15px);
	}
}

@-moz-keyframes right {
	0% {
		-moz-transform: translate(-15px);
	}
	50% {
		-moz-transform: translate(15px);
	}
	100% {
		-moz-transform: translate(-15px);
	}
}

@-moz-keyframes left {
	0% {
		-moz-transform: translate(15px);
	}
	50% {
		-moz-transform: translate(-15px);
	}
	100% {
		-moz-transform: translate(15px);
	}
}

@keyframes right {
	0% {
		transform: translate(-15px);
	}
	50% {
		transform: translate(15px);
	}
	100% {
		transform: translate(-15px);
	}
}

@keyframes left {
	0% {
		transform: translate(15px);
	}
	50% {
		transform: translate(-15px);
	}
	100% {
		transform: translate(15px);
	}
}
    </style>
</head>
<body>
    <h1>Chat with ChatGPT</h1>
    <form action="/chat" method="post">
        <label for="user_input">Enter your message:</label><br>
        <input type="text" id="user_input" name="user_input" required><br><br>
        <input type="submit" value="Send">
    </form>
    {% if assistant_reply %}
    <h2>ChatGPT's Response:</h2>
    <pre>{{ assistant_reply }}</pre>
    {% endif %}
    <div class="container">
  <div class="ball"></div>
  <div class="ball"></div>
  <div class="ball"></div>
  <div class="ball"></div>
  <div class="ball"></div>
  <div class="ball"></div>
  <div class="ball"></div>
</div>
</body>
</html>
'''

@app.route('/')
async def index():
    # Render the initial HTML page with no response yet
    return await render_template_string(html_template)

@app.route('/chat', methods=['POST'])
async def chat():
    try:
        # Get user input from the form
        form_data = await request.form
        user_input = form_data['user_input']

        # Interact with OpenAI API
        assistant = client.beta.assistants.create(
            name="quiz master",
            description="You are a trivia master.",
            model="gpt-4-turbo",
            tools=[{"type": "code_interpreter"}]
        )
        thread = client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": "Create a 10 question quiz about the NFL in the 2010s, for each question allow the user to select an answer and after they complete the quiz give them feedback on if they were right or wrong along with the inital question. The quiz should appear on the inital screen"
                }
            ]
        )
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=""
        )
        while run.status != "completed":
            time.sleep(5)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"\t\t{run}")

        if run.status == 'completed':
            messages = client.beta.threads.messages.list(
                thread_id=thread.id).model_dump_json()

        # Extract the assistant's response
        json_data = json.loads(messages)
        values = []
        for item in json_data['data']:
            values.append(item['content'][0]['text']['value'])
            values = values.pop()
            assistant_response = values
        # Render the HTML page with the ChatGPT response
            return await render_template_string(html_template, assistant_reply=assistant_response)

    except Exception as e:
        # Log any errors
        app.logger.error(f"Error: {e}")
        return await render_template_string(html_template, assistant_reply="Something went wrong, please try again.")


if __name__ == '__main__':
    app.run(debug=True)
