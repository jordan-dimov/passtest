from collections import deque

import openai


def gpt_chat(messages):
    response = openai.ChatCompletion.create(
        # model='gpt-3.5-turbo',
        model="gpt-4",
        # model="gpt-4-32k",
        messages=messages,
    )
    return response.choices[0].message.content.strip()


class ChatMem:
    def __init__(self, system_msg=None, mem_size=50):
        self.mem = deque([], mem_size)
        if system_msg:
            self.mem.appendleft({"role": "system", "content": system_msg})

    def add(self, role, content):
        self.mem.appendleft({"role": role, "content": content})

    def get(self):
        return list(reversed(self.mem))

    def clear(self):
        self.mem.clear()

    def __repr__(self):
        return f"ChatMem({len(self.mem)} messages)"

    def __str__(self):
        return self.__repr__()

    def __len__(self):
        return len(self.mem)
