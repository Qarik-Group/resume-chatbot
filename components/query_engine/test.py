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

from common import constants, googleai_tools, llm_tools
from common.log import Logger, log

logger = Logger(__name__).get_logger()
logger.info('Initializing...')


@log
def test_queries(query_engine) -> None:
    """Test sample queries."""
    queries = [
        'What are Roman Kharkovski skills?',
        'What is the current job title of Steven Kim?',
        'Does John Bishop have Java experience?',
        'Compare and contrast skills of Atilla Guzel and Michael Kharkovski.',
        'What is the current job title of Roman Kharkovski?',
        'What was the job title of Roman Kharkovski prior to joining Qarik?',
        'What are the three most recent job titles of Roman Kharkovski?',
        # 'Give me a list of all people who have provided their resumes.',
        # 'What is Roman Kharkovski\'s email?',
        # 'What are the main skills for Roman Kharkovski?',
        # 'How many total years of experience does Roman Kharkovski have?',
        # 'Did Steven Kim work for Google?',
        # 'What companies Roman Kharkovski worked for?',
        # 'Does Roman Kharkovski have Java skills?',
        # 'Compare and contrast the skills of Roman Kharkovski and Steven Kim.',
        # 'List all people with Java skills.',
        # 'Do any people have SAP or COBOL skills?',
        # 'When did Roman Kharkovski start working for IBM?',
        # 'When did Roman Kharkovski start working for Google?',
        # 'What is the most common skill among all people?',
        # 'Tell me about Roman Kharkovski strengths and weaknesses?',
        # 'Among all people, who has the most experience with Java, Google Cloud, and Kubernetes?',
        # 'How many people have skills in Python and Machine Learning?',
        # 'Where did Roman Kharkovski work the longest?',
        # 'Give me a summary of skills of all people.',
    ]

    responses = []
    errors = []
    error_count: int = 0

    for query in queries:
        try:
            print(f'Query: {query}')
            responses.append((query, str(query_engine.query(query))))
            print(f'\nResponse: {responses[-1]}\n\n')
        except Exception as e:
            logger.error('Error processing query: %s, error: %s', query, e)
            error_count += 1
            errors.append((query, str(e)))

    print('\x1b[0;30;42m')
    print('------------------------------')
    print('  Responses that succeeded:')
    print('------------------------------')
    print('\x1b[0;37;42m')
    for response in responses:
        print('*******************************************************************************')
        print(f'> QUERY: {response[0]} \n> RESPONSE: {response[1]}')

    print('\x1b[0;30;41m')
    print('------------------------------')
    print('  Responses that failed:')
    print('------------------------------')
    print('\x1b[0;37;41m')
    for error in errors:
        print('*******************************************************************************')
        print(f'> QUERY: {error[0]} \n> RESPONSE: {error[1]}')

    print('\x1b[0;30;40m')
    print('*******************************************************************************')
    print(f'Total questions: {len(queries)}\nErrors: {error_count}')
    print('*******************************************************************************')
    # Reset colors
    print('\x1b[0m')


@log
def main():
    """Main function of the app."""
    print('')
    print('*************************************************************************')
    print('********************** Testing Skills Query Bot *************************')
    print('*************************************************************************')
    # provider = constants.LlmProvider.GOOGLE_PALM
    provider = constants.LlmProvider.OPEN_AI
    gpt_query_engine = llm_tools.get_resume_query_engine(
        index_dir='dev/tmp/embeddings', resume_dir='dev/tmp/resumes', provider=provider)

    if gpt_query_engine is None:
        logger.error('No resumes found in the database. Please upload resumes or connect to the database.')
        return

    test_queries(gpt_query_engine)
    return
    test_queries(googleai_tools)

    print('\n\nINTERACTIVE MODE:')
    while True:
        print('*******************************************************************************')
        query_text = input('Ask your question: ')
        # response = index.query(query_text)
        # print(f'ANSWER: {response} (last_token_usage={index.llm_predictor.last_token_usage})')
        if query_text:
            print('Generating answer...')
            try:
                # Test ChatGPT
                gpt_response = gpt_query_engine.query(query_text)
                # TODO - experiment with different prompt tunings
                # response = query_engine.query(query_text + constants.QUERY_SUFFIX)
                print(f'GPT response: {gpt_response}')
                # Test Google AI
                goog_response = googleai_tools.query(query_text)
                print(f'Google response: {goog_response}')
            except Exception as e:
                logger.error('Error processing query: %s, error: %s', query_text, e)
                print(f'ERROR: {e}')


# Run the app
if __name__ == '__main__':
    main()
