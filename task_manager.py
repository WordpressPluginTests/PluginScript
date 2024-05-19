
import docx
from queue import PriorityQueue
import json
import logging
import time
import re
import requests
from bs4 import BeautifulSoup

def load_tasks_from_document(file_path):
    doc = docx.Document(file_path)
    tasks = []
    current_task = None
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith("Task") and not current_task:
            current_task = {'title': text, 'subtasks': []}
        elif text.startswith("Task") and current_task:
            tasks.append(current_task)
            current_task = {'title': text, 'subtasks': []}
        elif current_task and text:
            current_task['subtasks'].append({'title': text, 'status': 'pending'})
    
    if current_task:
        tasks.append(current_task)
    
    return tasks

def determine_priority(task):
    if 'Research' in task['title']:
        return 1
    if 'Develop' in task['title']:
        return 2
    if 'Test' in task['title']:
        return 3
    return 4

def prioritize_tasks(tasks):
    queue = PriorityQueue()
    for task in tasks:
        priority = determine_priority(task)
        queue.put((priority, task))
    return queue

def perform_internet_search(query):
    """Perform an internet search and return summarized findings."""
    search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    findings = []
    for result in soup.find_all('div', class_='BNeawe s3v9rd AP7Wnd'):
        text = result.get_text()
        if text not in findings:
            findings.append(text)
    
    return findings[:5]  # Return the first 5 findings for brevity

def perform_subtask(subtask):
    print(f"Executing subtask: {subtask['title']}")
    if 'Research' in subtask['title']:
        query = re.search(r'Research (.*)', subtask['title']).group(1)
        findings = perform_internet_search(query)
        subtask['findings'] = findings
    time.sleep(1)

def log_task_execution(task, subtask):
    logging.info(f"Executing {subtask['title']} of {task['title']}")

def notify_completion(task):
    print(f"Notification: Task {task['title']} completed")

def execute_task(task):
    for subtask in task['subtasks']:
        if subtask['status'] == 'pending':
            log_task_execution(task, subtask)
            perform_subtask(subtask)
            subtask['status'] = 'completed'
    notify_completion(task)

def save_task_progress(tasks, file_path):
    with open(file_path, 'w') as file:
        json.dump(tasks, file, indent=4)

if __name__ == "__main__":
    logging.basicConfig(filename='task_execution.log', level=logging.INFO)
    
    tasks = load_tasks_from_document('newList.docx')
    task_queue = prioritize_tasks(tasks)

    while not task_queue.empty():
        _, task = task_queue.get()
        execute_task(task)
        save_task_progress(tasks, 'tasks_progress.json')
