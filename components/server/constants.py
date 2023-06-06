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

# from datetime import timezone
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
# TIMEZONE: timezone = timezone.utc
# """Normalize all dates to this timezone across the entire project."""

#########################################################
# LLM specific settings
#########################################################
MODEL_NAME = 'gpt-3.5-turbo'
# MODEL_NAME = 'gpt-4'
"""LLM model name to be used."""

MAX_KEYWORDS_PER_CHUNK = 100
"""Maximum number of keywords per chunk for Complex Query Graph."""

CHUNK_SIZE_LIMIT = 2048
"""Maximum number of characters per chunk for Complex Query Graph."""

TEMPERATURE = 0
"""Temperature for LLM model."""

MAX_TOKENS = 1024
"""Maximum number of tokens for LLM model."""

QUERY_SUFFIX = '\nIf you can not find the answer, answer the query with the best of your knowledge.'
"""Suffix to be added to the query."""

# Text QA templates
# DEFAULT_TEXT_QA_PROMPT_TMPL = ('Context information is below. \n'
#                                '---------------------\n'
#                                '{context_str}'
#                                '\n---------------------\n'
#                                'Given the context information answer the following question '
#                                '(if you don't know the answer, use the best of your knowledge): {query_str}\n')
# TEXT_QA_TEMPLATE = QuestionAnswerPrompt(DEFAULT_TEXT_QA_PROMPT_TMPL)

# Refine templates
# DEFAULT_REFINE_PROMPT_TMPL = (
#     'The original question is as follows: {query_str}\n'
#     'We have provided an existing answer: {existing_answer}\n'
#     'We have the opportunity to refine the existing answer '
#     '(only if needed) with some more context below.\n'
#     '------------\n'
#     '{context_msg}\n'
#     '------------\n'
#     'Given the new context and using the best of your knowledge, improve the existing answer. '
#     'If you can't improve the existing answer, just repeat it again. '
#     'Do not mention that you've read the above context.')
# DEFAULT_REFINE_PROMPT = RefinePrompt(DEFAULT_REFINE_PROMPT_TMPL)

# CHAT_REFINE_PROMPT_TMPL_MSGS = [
#     HumanMessagePromptTemplate.from_template('{query_str}'),
#     AIMessagePromptTemplate.from_template('{existing_answer}'),
#     HumanMessagePromptTemplate.from_template(
#         'We have the opportunity to refine the above answer '
#         '(only if needed) with some more context below.\n'
#         '------------\n'
#         '{context_msg}\n'
#         '------------\n'
#         'Given the new context and using the best of your knowledge, improve the existing answer. '
#         'If you can't improve the existing answer, just repeat it again. '
#         'Do not mention that you've read the above context.'),
# ]

# CHAT_REFINE_PROMPT_LC = ChatPromptTemplate.from_messages(CHAT_REFINE_PROMPT_TMPL_MSGS)

# CHAT_REFINE_PROMPT = RefinePrompt.from_langchain_prompt(CHAT_REFINE_PROMPT_LC)

# refine prompt selector
# DEFAULT_REFINE_PROMPT_SEL_LC = ConditionalPromptSelector(
#     default_prompt=DEFAULT_REFINE_PROMPT.get_langchain_prompt(),
#     conditionals=[(is_chat_model, CHAT_REFINE_PROMPT.get_langchain_prompt())],
# )

# REFINE_TEMPLATE = RefinePrompt(langchain_prompt_selector=DEFAULT_REFINE_PROMPT_SEL_LC)

# DEFAULT_TERM_STR = ('Make a list of terms and definitions that are defined in the context, '
#                     'with one pair on each line. '
#                     'If a term is missing it's definition, use your best judgment. '
#                     'Write each line as as follows:\nTerm: <term> Definition: <definition>')
