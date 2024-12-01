from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain.prompts import PromptTemplate
from typing import Callable, Generator

from llm import invoke_llm, invoke_llm2
from utils import PROMPTS_DIR, get_category_from_pronpt_file, get_prompt_files, timeit

prompt_files = get_prompt_files()

def moderate_post(post: str, category_to_check: str=None) -> str|Generator[str, None, None]:
    print(f'Post: {post}')
    alerts: list[str] = []

    with ThreadPoolExecutor(max_workers=2) as executor: # process 2 prompts at a time, using llm and llm2 in parallel
        futures = []
        for i, prompt_file in enumerate(prompt_files):
            category = get_category_from_pronpt_file(prompt_file)
            if category_to_check and category_to_check != category:
                continue # skip this category
            with open(f'{PROMPTS_DIR}/{prompt_file}', 'r', encoding='utf-8') as f:
                prompt = f.read()
            prompt = f"Context: {category}\n{prompt}\nThe negative label should be used ONLY in the *DIRECT* context of the above. Do NOT label as negative based on a different context than the above, even if related. If the post is not EXPLICITLY related to the context, do NOT use negative. You are not certified to make judgements on other contexts."
            prompt = PromptTemplate.from_template(prompt)
            prompt = prompt.invoke({'post': post}).to_string()

            invoke_func = invoke_llm if i % 2 == 0 else invoke_llm2
            futures.append(executor.submit(_process_prompt, invoke_func, prompt, category))

        for future in as_completed(futures):
            try:
                category, response = future.result()
                print(f'Response for [{category.upper()}]: {response}')

                lines = response.split('\n')
                label_line = _find_line_with(lines, '*label')

                if label_line and 'negative' in label_line.casefold():
                    reason_line = _find_line_with(lines, '*reason')
                    if reason_line:
                        reason = reason_line.replace(' post ', ' statement ', 1).strip()
                        alert = f'{category.upper()} ALERT {reason}'
                        yield alert
                        alerts.append(alert)

            except:
                # just skip this prompt (exception already logged)
                pass

    summary = ''
    if len(alerts) > 1:
        alerts = '\n'.join(alerts).strip()
        summary = f"Safe Speech Alerts Summary:\n{alerts}"
    elif len(alerts) == 1:
        summary = '' # no need to summarize if only 1 alert
    elif category_to_check:
        summary = f'Speech is <b>safe</b> for category <b>{category_to_check}</b>. Pls. check other categories.'
    else:
        summary = 'Speech is safe✅'
    print(summary)

    yield summary

def _process_prompt(invoke_func: Callable, prompt: str, category: str) -> tuple[str, str]:
    try:
        response = invoke_func(prompt)
        response = response.content
        return category, response
    except Exception as e:
        print(f'Error for {category=}, {prompt=}: {e}')
        raise

def _find_line_with(lines: list[str], match: str) -> str|None:
    label_line = [line for line in lines if match in line.casefold()]
    label_line = label_line[0] if label_line else None
    return label_line

if __name__ == '__main__':
    # test usage
    @timeit
    def call_moderate_post(post) -> str:
        for alert in moderate_post(post):
            print(f"{'*'*10}YIELD: {alert=}")

    response = call_moderate_post('i forbade my son going to basketball practice when i learned his coach is gay')
#    response = call_moderate_post("people who can't finish high school shouldn't have kids because the kids will grow up poor")
#    response = call_moderate_post("the blind woman stepped on her dog's own poo, it was so funny lol")
#    response = call_moderate_post('she is the youngest member on our team but she still does her job like a pro')
#    response = call_moderate_post('she is very old to still be doing that job')
