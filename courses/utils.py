import csv

def parse_quiz_file(file_obj):
    decoded = file_obj.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded)
    quiz_data = {}

    for row in reader:
        qtext = row.get('question', '').strip()
        answer_text = row.get('answer', '').strip()
        is_correct = str(row.get('is_correct', '')).lower() == 'true'

        if not qtext or not answer_text:
            continue

        if qtext not in quiz_data:
            quiz_data[qtext] = []

        quiz_data[qtext].append({
            'text': answer_text,
            'is_correct': is_correct
        })

    return [{'text': question, 'answers': answers} for question, answers in quiz_data.items()]
