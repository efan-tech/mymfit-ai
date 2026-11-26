import json

from main import ask_ai


print("\n===================================")
print("          MYMFIT AI")
print("     Your Personal Fitness Coach")
print("===================================")


question = input("\nYou: ")

print("\nMYMFIT AI is thinking...\n")
messages = [{ "role": "user", "content": question }]

result = ask_ai(messages)
response = result[0] if isinstance(result, tuple) else result



if "error" in response:

    print("Error:", response["error"])
elif "message" not in response or "recommendations" not in response or "next_question" not in response or "safety_note" not in response:
    print("raw response:", result)
else:


    print("MYMFIT AI:")

    print(response["message"])

    print("\nRECOMMENDATIONS:")

    for item in response["recommendations"]:

        print("\n-", item["title"])
        print(item["details"])

    print("\nFOLLOW-UP QUESTION:")

    print(response["next_question"])

    print("\nSAFETY NOTE:")

    print(response["safety_note"])