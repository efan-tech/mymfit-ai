import os
import json

from dotenv import load_dotenv
from groq import Groq

from ai.prompts import SYSTEM_PROMPT, SUMMARY_PROMPT

from cache.cache_manager import (
    initialize_cache,
    generate_cache_key,
    get_cached_response,
    save_cached_response
)


# LOAD ENVIRONMENT VARIABLES
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("Groq API key not found!")

client = Groq(api_key=API_KEY)


# MODEL CONFIGURATION
MODEL = "openai/gpt-oss-20b"


# INITIALIZE CACHE
initialize_cache()


# ASK AI WITH AUTOMATIC CACHING
def ask_ai(conversation_history):

    try:

        # GET LATEST USER QUESTION
        latest_question = conversation_history[-1]["content"]

        # GET PREVIOUS CONVERSATION CONTEXT
        previous_history = conversation_history[:-1]

        # GENERATE CACHE FINGERPRINT
        cache_key = generate_cache_key(
            latest_question,
            previous_history,
            SYSTEM_PROMPT,
            MODEL
        )

        # CHECK LOCAL CACHE
        cached_response = get_cached_response(cache_key)

        if cached_response is not None:

            print("\n[CACHE HIT] Retrieved answer locally.")

            return cached_response, json.dumps(cached_response)

        # NO CACHE FOUND
        print("\n[CACHE MISS] Contacting Groq API...")

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

        messages.extend(conversation_history)

        # SEND REQUEST TO GROQ
        response = client.chat.completions.create(

            model=MODEL,

            messages=messages,

            temperature=0.7,

            max_completion_tokens=1000,

            response_format={"type": "json_object"}

        )

        answer = response.choices[0].message.content

        parsed_answer = json.loads(answer)

        # RECORD TOKEN USAGE
        usage = response.usage

        input_tokens = usage.prompt_tokens if usage else 0

        output_tokens = usage.completion_tokens if usage else 0

        # SAVE ANSWER IN CACHE
        save_cached_response(

            cache_key,

            latest_question,

            parsed_answer,

            input_tokens,

            output_tokens

        )

        print("\n[NEW RESPONSE] Answer saved in local cache.")

        return parsed_answer, answer

    except json.JSONDecodeError:

        return {
            "error": "Invalid JSON response from AI."
        }, None

    except Exception as error:

        return {
            "error": str(error)
        }, None


# GENERATE SESSION SUMMARY
def generate_summary(conversation_history):

    try:

        messages = [

            {
                "role": "system",
                "content": SUMMARY_PROMPT
            },

            {
                "role": "user",
                "content": json.dumps(
                    conversation_history,
                    ensure_ascii=False
                )
            }

        ]

        response = client.chat.completions.create(

            model=MODEL,

            messages=messages,

            temperature=0.3,

            max_completion_tokens=1200,

            response_format={"type": "json_object"}

        )

        answer = response.choices[0].message.content

        return json.loads(answer)

    except Exception as error:

        print("Summary generation failed:", error)

        return {
            "error": "Summary could not be generated."
        }
