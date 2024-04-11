import json
import uuid
import time
import random

def convert_json(processed_data):
    converted_chat = {
        "id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4()),
        "title": "Converted Chat",
        "chat": {
            "id": "",
            "title": "Converted Chat",
            "models": ["llama2:latest"],
            "options": {},
            "messages": [],
            "history": {
                "messages": {},
                "currentId": None
            },
            "tags": [],
            "timestamp": int(time.time())
        },
        "timestamp": int(time.time()),
        "share_id": None
    }

    parent_id = None
    prev_timestamp = None
    base_timestamp = int(time.time())

    for item in processed_data:
        question = item["question"]
        answer = item["answer"]

        user_message_id = str(uuid.uuid4())
        user_message = {
            "id": user_message_id,
            "parentId": parent_id,
            "childrenIds": [],
            "role": "user",
            "content": question,
            "timestamp": base_timestamp
        }
        converted_chat["chat"]["messages"].append(user_message)
        converted_chat["chat"]["history"]["messages"][user_message_id] = user_message

        assistant_message_id = str(uuid.uuid4())
        assistant_message = {
            "parentId": user_message_id,
            "id": assistant_message_id,
            "childrenIds": [],
            "role": "assistant",
            "content": answer,
            "model": "llama2:latest",
            "timestamp": base_timestamp + 1,
            "done": True,
            "context": None,
            "info": {
                "total_duration": len(answer) * 1000000,
                "load_duration": len(answer) * 100,
                "prompt_eval_duration": len(question) * 1000,
                "eval_count": len(answer) * 10,
                "eval_duration": len(answer) * 1000000
            }
        }
        user_message["childrenIds"].append(assistant_message_id)
        converted_chat["chat"]["messages"].append(assistant_message)
        converted_chat["chat"]["history"]["messages"][assistant_message_id] = assistant_message

        parent_id = assistant_message_id
        prev_timestamp = assistant_message["timestamp"]
        base_timestamp += 16

    converted_chat["chat"]["history"]["currentId"] = converted_chat["chat"]["messages"][-1]["id"]
    return converted_chat

def process_qa_pairs(input_file, output_file):
    with open(input_file, "r") as file:
        processed_data = json.load(file)

    num_pairs = len(processed_data)
    print(f"Detected {num_pairs} question-answer pairs. Enter the number of randomly selected pairs, or enter 0 to select all.")
    print("Warning: Importing too many chat histories at once may slow down the device! Before importing chat history, please check the maximum context length supported by the model.")

    while True:
        try:
            num_selected = int(input("Please enter the number of selected question-answer pairs (0-{}): ".format(num_pairs)))
            if num_selected < 0 or num_selected > num_pairs:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    if num_selected == 0:
        selected_data = processed_data
    else:
        selected_data = random.sample(processed_data, num_selected)

    converted_chat = convert_json(selected_data)

    with open(output_file, "w") as file:
        json.dump([converted_chat], file, indent=4)

    print("Conversion completed! {} question-answer pairs have been written to {}.".format(len(selected_data), output_file))

process_qa_pairs("input.json", "converted_chat.json")