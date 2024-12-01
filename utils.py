import decorator
import os
import time

PROMPTS_DIR = 'prompts'
PROMPT_FILE_EXT = '.PROMPT.txt'

def get_prompt_files() -> list[str]:
    return [file_name for file_name in os.listdir(PROMPTS_DIR) if file_name.endswith(PROMPT_FILE_EXT)]

def get_category_from_pronpt_file(prompt_file: str) -> str:
    return prompt_file.replace(PROMPT_FILE_EXT, '')

@decorator.decorator
def timeit(func, *args, **kwargs):
    start = time.time()
    try:
        return func(*args, **kwargs)
    except Exception as e:
        raise e
    finally:
        end = time.time()
        print(f'[{func.__name__}] took {end - start:.2f} seconds')
