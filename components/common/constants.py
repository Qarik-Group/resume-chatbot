# Copyright 2023 Qarik Group, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Project wide settings and constants."""

from datetime import timezone
from enum import Enum
# from langchain.chains.prompt_selector import ConditionalPromptSelector, is_chat_model
# from langchain.prompts.chat import AIMessagePromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate
# from llama_index.prompts.prompts import QuestionAnswerPrompt, RefinePrompt

#########################################################
# Definitions of frequently used units of measurement
#########################################################
SECOND: int = 1
"""One second."""

MINUTE: int = 60
"""Seconds in a minute."""

HOUR: int = 60 * 60
"""Seconds in an hour."""

DAY: int = HOUR * 24
"""Seconds in a single day."""

WEEK: int = DAY * 7
"""Seconds in a week."""

MONTH: int = WEEK * 4
"""Seconds in a month (approximate)."""

YEAR: int = DAY * 365
"""Seconds in a year (approximate)."""

#########################################################
# General settings
#########################################################
TIMEZONE: timezone = timezone.utc
"""Normalize all dates to this timezone across the entire project."""

#########################################################
# LLM specific settings
#########################################################
class LlmProvider(Enum):
    GOOGLE_PALM = 1
    OPEN_AI = 2
"""Which LLM provider to use."""

# GPT_MODEL = 'text-davinci-003'
# GPT_MODEL = 'gpt-3.5-turbo'
GPT_MODEL: str = 'gpt-4'
"""Open AI model name to be used."""

MAX_KEYWORDS_PER_CHUNK: int = 100
"""Maximum number of keywords per chunk for Complex Query Graph."""

CHUNK_SIZE: int = 1024
"""Maximum number of characters per chunk for Complex Query Graph."""

TEMPERATURE = 0
"""Temperature for LLM model."""

SIMILARITY_TOP_K: int = 50
"""Number of top similar documents to retrieve."""

# Text QA templates
# DEFAULT_TEXT_QA_PROMPT_TMPL = ('Context information is below. \n'
#                                '---------------------\n'
#                                '{context_str}'
#                                '\n---------------------\n'
#                                'Given the context information answer the following question '
#                                '(if you don't know the answer, use the best of your knowledge): {query_str}\n')
# TEXT_QA_TEMPLATE = QuestionAnswerPrompt(DEFAULT_TEXT_QA_PROMPT_TMPL)
