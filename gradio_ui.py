import gradio as gr

from typing import Generator

from post_moderator import moderate_post, prompt_files
from utils import get_category_from_pronpt_file

APP_NAME = 'My Speech Safety Check'
ALL_CATEGORIES_INDICATOR = '[All]'

# load categories
categories = [ALL_CATEGORIES_INDICATOR]
for prompt_file in prompt_files:
    category = get_category_from_pronpt_file(prompt_file)
    categories.append(category)

bulletpt = '\u2022'

GREETING = \
f'''
Welcome🕊️ enter a post below and I'll check it for {bulletpt}safe speech{bulletpt} before you post it <i>for real</i>.

You can choose a specific safe speech category to check for, or use <i>{ALL_CATEGORIES_INDICATOR}</i>.
'''.strip()

# send_button click handler
def submit_message(message: str, category: str, history: list[tuple[str, str]]) -> Generator[tuple[list, str], None, None]:
    if not message:
        yield history, None
        return

    print(f'[category]: {category} [post]: {message}')

    if category and category != ALL_CATEGORIES_INDICATOR:
        pass #TODO

    history.append((message, None))
    yield history, None

    for alert in moderate_post(message):
        history.append((None, alert))
        yield history, None

# clear_button click handler
def clear_messages() -> tuple[list[tuple[str, str]], str, str]:
    return [(None, GREETING)], None, ALL_CATEGORIES_INDICATOR

with gr.Blocks(title=APP_NAME, theme=gr.themes.Citrus(), css='''
    footer {visibility: hidden}

    /* for dropdown icon: increase size, make colour stronger */
    .wrap-inner .icon-wrap svg {
        width: 48px !important;
        height: 48px !important;
        fill: #0077b6 !important;
    }

    /* remove clear button in chatbot */
    button[aria-label="Clear"] {
        display: none !important;
    }
            ''') as demo:
    gr.Markdown(F'<h1 style="text-align:center;">{APP_NAME}</h1>')

    chatbot = gr.Chatbot(
        label='Keep Safe',
        height='55vh',
        show_copy_all_button=True,
        value=[(None, GREETING)]
    )

    with gr.Row(variant='panel'):
        with gr.Column(scale=6):
            msg = gr.Textbox(autofocus=True, label='Post', lines=4)
        with gr.Column(scale=2):
            category_dropdown = gr.Dropdown(label=f'Category', choices=categories)
            send_button = gr.Button('Check It☑️')

    with gr.Row():
        clear_button = gr.Button('Clear')

    send_button.click(submit_message, inputs=[msg, category_dropdown, chatbot], outputs=[chatbot, msg])
    clear_button.click(clear_messages, outputs=[chatbot, msg, category_dropdown])

demo.launch(server_name='0.0.0.0')
