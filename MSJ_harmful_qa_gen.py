import json
import logging
import os
from tqdm import tqdm
import requests
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with open('config.json') as f:
    config = json.load(f)

with open('prompts.json') as f:
    prompts = json.load(f)

MODEL_NAME = config['MODEL_NAME']
OUTPUT_DIR = config['OUTPUT_DIR']
API_URL = config['REQUEST_POST']

os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_questions(num_questions, question_prompts):
    questions = []
    unique_questions = set()
    
    with tqdm(total=num_questions, desc="Generating Questions", unit="question") as pbar:
        while len(questions) < num_questions:
            question_prompt = random.choice(question_prompts)
            messages = [{"role": "user", "content": question_prompt}]
            response = send_api_request(messages)
            question = response['content'].strip()
            
            if question and question not in unique_questions:
                questions.append(question)
                unique_questions.add(question)
                pbar.update(1)
        
    temp_file = os.path.join(OUTPUT_DIR, "qa_temp.json")
    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(questions, file, indent=2, ensure_ascii=False)
    logging.info(f"{len(questions)} questions saved to {temp_file}")
                
    return questions

def generate_answers(questions, answer_prompts):
    answers = []
    for question in tqdm(questions, desc="Generating Answers", unit="answer"):
        answer_prompt = random.choice(answer_prompts)
        input_for_model = f"{answer_prompt} Q: {question}"
        messages = [{"role": "user", "content": input_for_model}]
        response = send_api_request(messages)
        answers.append(response['content'])
    return answers

def send_api_request(messages):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True
    }
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    output = ""
    for line in response.iter_lines():
        body = json.loads(line)
        if "error" in body:
            raise Exception(body["error"])
        if body.get("done") is False:
            message = body.get("message", "")
            content = message.get("content", "")
            output += content
            print(content, end="", flush=True)
        if body.get("done", False):
            message["content"] = output
            return message

def main():
    while True:
        print("\nWelcome to the Many-Shots Jailbreak Q&A Pair Generator!")
        print("Please select an option:")
        print("1. Generate Q&A pairs with random prompts.")
        print("2. Generate Q&A pairs about Hate.")
        print("3. Generate Q&A pairs about Sexual.")
        print("4. Generate Q&A pairs about Violence.")
        print("5. Generate Q&A pairs about Self-harm.")
        print("Type 'quit' or 'exit' to end the program.")

        choice = input("\nYour choice: ").strip().lower()
        if choice in ["quit", "exit"]:
            print("Thank you for using the Q&A Pair Generator. Goodbye!")
            break

        try:
            num_pairs = int(input("Enter the number of Q&A pairs to generate: "))
            if num_pairs <= 0:
                raise ValueError("Number of Q&A pairs must be a positive integer.")

            if choice == "1":
                topic_choices = ["2", "3", "4", "5"]
                question_prompts = [prompts[choice]['question'] for choice in topic_choices]
                answer_prompts = [prompts[choice]['answer'] for choice in topic_choices]
                questions = generate_questions(num_pairs, question_prompts)
                answers = generate_answers(questions, answer_prompts)
            else:
                question_prompt = prompts[choice]['question']
                answer_prompt = prompts[choice]['answer']
                questions = generate_questions(num_pairs, [question_prompt])
                answers = generate_answers(questions, [answer_prompt])

            qa_pairs = [{'question': q, 'answer': a} for q, a in zip(questions, answers)]

            logging.info(f"Generated {len(qa_pairs)} Q&A Pairs.")
            for pair in tqdm(qa_pairs, desc="Displaying Q&A pairs", unit="pair"):
                print(f"Question: {pair['question']}")
                print(f"Answer: {pair['answer']}")
                print()

            output_file = os.path.join(OUTPUT_DIR, "qa_pairs.json")
            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(qa_pairs, file, indent=2, ensure_ascii=False)
            logging.info(f"{len(qa_pairs)} Q&A pairs saved to {output_file}")

        except ValueError as e:
            logging.error(str(e))
            continue

if __name__ == "__main__":
    main()