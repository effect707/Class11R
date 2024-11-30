import json
import csv
from datetime import datetime
import os
from babel.dates import format_datetime
import re


class Note:
    def __init__(self, note_id, title, content, timestamp=None):
        self.id = note_id
        self.title = title
        self.content = content
        self.timestamp = timestamp or self.current_timestamp()

    @staticmethod
    def current_timestamp():
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    def update(self, title=None, content=None):
        if title:
            self.title = title
        if content:
            self.content = content
        self.timestamp = self.current_timestamp()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["id"], data["title"], data["content"], data["timestamp"])


class NoteManager:

    def __init__(self, storage_file='notes.json'):
        self.storage_file = storage_file
        self.notes = self.load_notes()

    def load_notes(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    return [Note.from_dict(note) for note in data]
                except json.JSONDecodeError:
                    print("Ошибка: файл JSON пустой или содержит ошибки. Он будет перезаписан.")
                    return []
        else:
            return []

    def save_notes(self):
        with open(self.storage_file, 'w', encoding='utf-8') as file:
            json.dump([note.to_dict() for note in self.notes], file, ensure_ascii=False, indent=4)

    def create_note(self, title, content):
        note_id = max([note.id for note in self.notes], default=0) + 1
        note = Note(note_id, title, content)
        self.notes.append(note)
        self.save_notes()
        return note

    def list_notes(self):
        return self.notes

    def view_note_details(self, note_id):
        return next((note for note in self.notes if note.id == note_id), None)

    def edit_note(self, note_id, title=None, content=None):
        note = self.view_note_details(note_id)
        if note:
            note.update(title, content)
            self.save_notes()
        return note

    def delete_note(self, note_id):
        if note_id == 'ALL':
            self.notes = []
            self.save_notes()
        elif any(i.id == note_id for i in self.notes):
            self.notes = [note for note in self.notes if note.id != note_id]
            self.save_notes()
            print(f'Заметка {note_id} успешно удалена')
        else:
            print(f'Заметка с {note_id} не найдена')

    def export_to_csv(self, csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "title", "content", "timestamp"])
            writer.writeheader()
            for note in self.notes:
                writer.writerow(note.to_dict())

    def import_from_csv(self, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                note = Note(
                    note_id=max([note.id for note in self.notes], default=0) + 1,
                    title=row["title"],
                    content=row["content"],
                    timestamp=row["timestamp"]
                )
                self.notes.append(note)
            print(row)
        self.save_notes()


class Task:
    def __init__(self, task_id, title, description, done=False, priority="Средний", due_date=None):
        self.id = task_id
        self.title = title
        self.description = description
        self.done = done
        self.priority = priority
        self.due_date = due_date

    def mark_done(self):
        self.done = True

    def update(self, title=None, description=None, priority=None, due_date=None):
        if title:
            self.title = title
        if description:
            self.description = description
        if priority:
            self.priority = priority
        if due_date:
            self.due_date = due_date

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "done": self.done,
            "priority": self.priority,
            "due_date": self.due_date
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["title"],
            data["description"],
            data["done"],
            data["priority"],
            data["due_date"]
        )


class TaskManager:
    def __init__(self, storage_file='tasks.json'):
        self.storage_file = storage_file
        self.tasks = self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    return [Task.from_dict(task) for task in data]
                except json.JSONDecodeError:
                    print("Ошибка: некорректный формат JSON. Файл будет перезаписан.")
                    return []
        else:
            return []

    def save_tasks(self):
        with open(self.storage_file, 'w', encoding='utf-8') as file:
            json.dump([task.to_dict() for task in self.tasks], file, ensure_ascii=False, indent=4)

    def add_task(self, title, description, priority="Средний", due_date=None):
        task_id = max([task.id for task in self.tasks], default=0) + 1
        task = Task(task_id, title, description, priority=priority, due_date=due_date)
        self.tasks.append(task)
        self.save_tasks()
        return task

    def list_tasks(self, filter_status=None, filter_priority=None, filter_due_date=None):
        filtered_tasks = self.tasks
        if filter_status:
            filtered_tasks = [task for task in filtered_tasks if task.done == filter_status]
        if filter_priority:
            filtered_tasks = [task for task in filtered_tasks if task.priority in filter_priority]
        if filter_due_date:
            filtered_tasks = [
                task for task in filtered_tasks if task.due_date and task.due_date <= filter_due_date
            ]
        return filtered_tasks

    def view_task_details(self, task_id):
        return next((task for task in self.tasks if task.id == task_id), None)

    def mark_task_done(self, task_id):
        task = self.view_task_details(task_id)
        if task:
            task.mark_done()
            self.save_tasks()
        return task

    def edit_task(self, task_id, title=None, description=None, priority=None, due_date=None):
        task = self.view_task_details(task_id)
        if task:
            task.update(title, description, priority, due_date)
            self.save_tasks()
        return task

    def delete_task(self, task_id):
        if task_id == 'ALL':
            self.tasks = []
        else:
            self.tasks = [task for task in self.tasks if task.id != task_id]
        self.save_tasks()

    def export_to_csv(self, csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "title", "description", "done", "priority", "due_date"])
            writer.writeheader()
            for task in self.tasks:
                writer.writerow(task.to_dict())

    def import_from_csv(self, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                task = Task(
                    task_id=int(row["id"]),
                    title=row["title"],
                    description=row["description"],
                    done=row["done"].lower() == 'true',
                    priority=row["priority"],
                    due_date=row["due_date"]
                )
                if not any(t.id == task.id for t in self.tasks):
                    self.tasks.append(task)
        self.save_tasks()


class Contact:
    def __init__(self, contact_id, name, phone=None, email=None):
        self.id = contact_id
        self.name = name
        self.phone = phone
        self.email = email

    def update(self, name=None, phone=None, email=None):
        if name:
            self.name = name
        if phone:
            self.phone = phone
        if email:
            self.email = email

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["name"],
            data.get("phone"),
            data.get("email")
        )


class ContactManager:
    def __init__(self, storage_file='contacts.json'):
        self.storage_file = storage_file
        self.contacts = self.load_contacts()

    def load_contacts(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    return [Contact.from_dict(contact) for contact in data]
                except json.JSONDecodeError:
                    print("Ошибка: некорректный формат JSON. Файл будет перезаписан.")
                    return []
        else:
            return []

    def save_contacts(self):
        with open(self.storage_file, 'w', encoding='utf-8') as file:
            json.dump([contact.to_dict() for contact in self.contacts], file, ensure_ascii=False, indent=4)

    def add_contact(self, name, phone=None, email=None):
        contact_id = max([contact.id for contact in self.contacts], default=0) + 1
        contact = Contact(contact_id, name, phone, email)
        self.contacts.append(contact)
        self.save_contacts()
        return contact

    def search_contacts(self, query):
        query = query.lower()
        return [
            contact for contact in self.contacts
            if query in (contact.name.lower() or "") or query in (contact.phone or "")
        ]

    def edit_contact(self, contact_id, name=None, phone=None, email=None):
        contact = self.get_contact_by_id(contact_id)
        if contact:
            contact.update(name, phone, email)
            self.save_contacts()
        return contact

    def delete_contact(self, contact_id):
        if contact_id == 'ALL':
            self.contacts = []
        else:
            self.contacts = [contact for contact in self.contacts if contact.id != contact_id]
        self.save_contacts()

    def get_contact_by_id(self, contact_id):
        return next((contact for contact in self.contacts if contact.id == contact_id), None)

    def export_to_csv(self, csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["id", "name", "phone", "email"])
            writer.writeheader()
            for contact in self.contacts:
                writer.writerow(contact.to_dict())

    def import_from_csv(self, csv_file):
        if os.path.exists(csv_file):
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    contact = Contact(
                        contact_id=int(row["id"]),
                        name=row["name"],
                        phone=row.get("phone"),
                        email=row.get("email")
                    )
                    if not any(c.id == contact.id for c in self.contacts):
                        self.contacts.append(contact)
            self.save_contacts()


class FinanceRecord:
    def __init__(self, record_id, amount, category, date, description):
        self.id = record_id
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "date": self.date,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["id"],
            data["amount"],
            data["category"],
            data["date"],
            data["description"],
        )


class FinanceManager:
    def __init__(self, file_path="finance.json"):
        self.file_path = file_path
        self.records = self.load_records()

    def load_records(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                data = json.load(file)
                return [FinanceRecord.from_dict(record) for record in data]
        return []

    def save_records(self):
        with open(self.file_path, "w") as file:
            json.dump([record.to_dict() for record in self.records], file, indent=4)

    def add_record(self, amount, category, date, description):
        record_id = max((record.id for record in self.records), default=0) + 1
        new_record = FinanceRecord(record_id, amount, category, date, description)
        self.records.append(new_record)
        self.save_records()

    def list_records(self, category=None):
        filtered = self.records
        if category:
            filtered = [record for record in filtered if record.category.lower() in category]
        return filtered

    def calculate_balance(self):
        return sum(record.amount for record in self.records)

    def get_record_by_id(self, record_id):
        return next((record for record in self.records if record.id == record_id), None)

    def generate_report(self, start_date, end_date: str):
        start = datetime.strptime(start_date, "%d-%m-%Y")
        end = datetime.strptime(end_date, "%d-%m-%Y")
        current_records = [record.to_dict() for record in self.records if
                           start <= datetime.strptime(record.date, "%d-%m-%Y") <= end]
        if current_records:
            print(current_records)
            file_path = f'report_{start_date}_{end_date}.csv'
            with open(file_path, "w", newline="") as file:
                fieldnames = ["id", "amount", "category", "date", "description"]
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for record in current_records:
                    writer.writerow(record)
            costs = sum([i['amount'] for i in current_records if i['amount'] < 0])
            profit = sum([i['amount'] for i in current_records])
            print(f'Финансовый отсчет с {start_date} по {end_date} \n'
                  f'- Общий доход: {format_number(profit + costs)} руб.\n'
                  f'- Общие расходы: {format_number(costs)} руб.\n'
                  f'- Баланс: {format_number(profit)}\n'
                  f'Подробная информация сохранена в файле {file_path}\n')
        else:
            print('Записи за указанный период не найдены.')

    def import_from_csv(self, file_path: str):
        with open(file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.add_record(float(row["amount"]), row["category"], row["date"], row["description"])

    def export_to_csv(self, file_path: str):
        with open(file_path, "w", newline="") as file:
            fieldnames = ["id", "amount", "category", "date", "description"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for record in self.records:
                writer.writerow(record.to_dict())

    def delete_record(self, record_id):
        if record_id == 'ALL':
            self.records = []
        else:
            self.records = [task for task in self.records if task.id != record_id]
        self.save_records()


def clear_console():
    print("\n" * 100)


def note_app():
    manager = NoteManager()

    while True:
        print(
            "\nМеню управления заметками:\n"
            "1. Добавить новую заметку\n"
            "2. Просмотреть список всех заметок\n"
            "3. Просмотреть подробности заметки\n"
            "4. Редактировать заметку\n"
            "5. Удалить заметку\n"
            "6. Экспорт заметок в CSV\n"
            "7. Импорт заметок из CSV\n"
            "8. Выход из приложения\n"
        )

        answer = input("Выберите действие (1-8): ").strip()
        clear_console()
        if answer == '1':  # Добавление заметки
            title = input("Введите заголовок заметки: ").strip()
            while not title:
                print("Ошибка: заголовок не может быть пустым.")
                title = input("Введите заголовок заметки: ").strip()

            content = input("Введите содержимое заметки (можно оставить пустым): ").strip()
            manager.create_note(title, content)
            clear_console()
            print("Заметка успешно добавлена.")

        elif answer == '2':  # Просмотр списка заметок
            notes = manager.list_notes()
            if notes:
                print("Список ваших заметок:")
                for note in notes:
                    print(f"ID: {note.id}, Заголовок: {note.title}, Дата: {note.timestamp}")
            else:
                print("У вас пока нет заметок.")

        elif answer == '3':  # Просмотр конкретной заметки
            while True:
                note_id = input("Введите ID заметки для просмотра или нажмите Enter для возврата в меню: ").strip()
                if not note_id:
                    clear_console()
                    break

                if not note_id.isdigit():
                    print("Ошибка: ID должен быть числом.")
                    continue

                note_id = int(note_id)
                clear_console()
                note = manager.view_note_details(note_id)
                if note:
                    details = note.to_dict()
                    formatted_date = format_datetime(
                        datetime.strptime(details['timestamp'], "%d-%m-%Y %H:%M:%S"),
                        "d MMMM yyyy года, HH:mm", locale="ru"
                    )
                    print(
                        f"\nДетали заметки (ID {note_id}):\n"
                        f"Заголовок: {details['title']}\n"
                        f"Содержимое: {details['content']}\n"
                        f"Последнее изменение: {formatted_date}\n"
                    )
                else:
                    print(f"Заметка с ID {note_id} не найдена.")

        elif answer == '4':  # Редактирование заметки
            note_id = input("Введите ID заметки для редактирования или нажмите Enter для возврата в меню: ").strip()
            if not note_id:
                continue

            if not note_id.isdigit():
                print("Ошибка: ID должен быть числом.")
                continue

            note_id = int(note_id)
            clear_console()
            if manager.view_note_details(note_id) is None:
                print(f"Заметка с ID {note_id} не найдена.")
            else:
                new_title = input("Введите новый заголовок заметки или нажмите Enter, чтобы оставить прежний: ").strip()
                new_content = input(
                    "Введите новое содержимое заметки или нажмите Enter, чтобы оставить прежнее: ").strip()
                manager.edit_note(note_id, title=new_title, content=new_content)
                clear_console()
                print("Заметка успешно обновлена.")

        elif answer == '5':  # Удаление заметки
            note_id = input(
                "Введите ID заметки для удаления, ALL для удаления всех заметок, или нажмите Enter для отмены: "
            ).strip()
            clear_console()
            if not note_id:
                continue
            elif note_id == "ALL":
                manager.delete_note("ALL")
                print("Все заметки успешно удалены.")
            elif not note_id.isdigit():
                print("Ошибка: ID должен быть числом.")
            else:
                note_id = int(note_id)
                manager.delete_note(note_id)
        elif answer == '6':  # Экспорт в CSV
            export_path = input("Введите путь для сохранения CSV-файла: ").strip()
            manager.export_to_csv(export_path)
            clear_console()
            print(f"Заметки успешно экспортированы в файл {export_path}.")

        elif answer == '7':  # Импорт из CSV
            import_path = input("Введите путь к CSV-файлу для импорта заметок: ").strip()
            if os.path.exists(import_path):
                manager.import_from_csv(import_path)
                clear_console()
                print(f"Заметки успешно импортированы из файла {import_path}.")
            else:
                print(f'Файл {import_path} не существует')

        elif answer == '8':  # Выход из приложения
            print("Выход из приложения. До свидания!")
            clear_console()
            break

        else:
            clear_console()
            print("Ошибка: выберите действие от 1 до 8.")


def task_app():
    manager = TaskManager()

    while True:
        print(
            "\nМеню управления задачами:\n"
            "1. Добавить новую задачу\n"
            "2. Просмотреть список задач\n"
            "3. Отметить задачу как выполненную\n"
            "4. Редактировать задачу\n"
            "5. Удалить задачу\n"
            "6. Экспорт задач в CSV\n"
            "7. Импорт задач из CSV\n"
            "8. Выход из приложения\n"
        )
        answer = input("Выберите действие (1-8): ").strip()
        clear_console()
        if answer == '1':  # Добавление новой задачи
            title = input("Введите название задачи: ").strip()
            while not title:
                print("Ошибка: название задачи не может быть пустым.")
                title = input("Введите название задачи: ").strip()

            content = input("Введите описание задачи (можно оставить пустым): ").strip()

            priority = input("Выберите приоритет задачи (Высокий/Средний/Низкий): ").capitalize()
            while priority not in ['Высокий', 'Средний', 'Низкий']:
                print("Ошибка: приоритет должен быть 'Высокий', 'Средний' или 'Низкий'.")
                priority = input("Выберите приоритет задачи (Высокий/Средний/Низкий): ").capitalize()

            due_time = input("Введите срок выполнения (ДД-ММ-ГГГГ): ").strip()
            while due_time:
                try:
                    due_time = datetime.strptime(due_time, "%d-%m-%Y").strftime("%d-%m-%Y")
                    break
                except ValueError:
                    print("Ошибка: неверный формат даты. Используйте ДД-ММ-ГГГГ.")
                    due_time = input("Введите срок выполнения (ДД-ММ-ГГГГ): ").strip()

            manager.add_task(title, content, priority=priority, due_date=due_time)
            clear_console()
            print("Задача успешно добавлена.")

        elif answer == '2':  # Просмотр задач с фильтрами
            print("Добавьте фильтры (или оставьте поля пустыми):")
            priority_filter = input("Фильтр по приоритету (Высокий/Средний/Низкий, через пробел): ").split()
            priority_filter = [p.capitalize() for p in priority_filter if
                               p.capitalize() in ['Высокий', 'Средний', 'Низкий']]

            done_filter = input("Фильтр по статусу (1 - выполненные, 0 - невыполненные): ").strip()
            while done_filter not in ['0', '1', '']:
                print("Ошибка: статус должен быть '1' или '0'.")
                done_filter = input("Фильтр по статусу (1 - выполненные, 0 - невыполненные): ").strip()

            due_filter = input("Фильтр по дате (показывать задачи до указанной даты, ДД-ММ-ГГГГ): ").strip()
            while due_filter:
                try:
                    due_filter = datetime.strptime(due_filter, "%d-%m-%Y")
                    break
                except ValueError:
                    print("Ошибка: неверный формат даты. Используйте ДД-ММ-ГГГГ.")
                    due_filter = input("Фильтр по дате (ДД-ММ-ГГГГ): ").strip()

            tasks = manager.list_tasks(filter_priority=priority_filter, filter_status=done_filter,
                                       filter_due_date=due_filter)
            if tasks:
                clear_console()
                print("\nСписок задач:")
                for task in tasks:
                    print(
                        f"ID: {task.id}, Название: {task.title}, Статус: {'Выполнена' if task.done else 'Не выполнена'}, "
                        f"Приоритет: {task.priority}, Срок: {task.due_date}")
            else:
                clear_console()
                print("Нет задач, соответствующих выбранным фильтрам.")

        elif answer == '3':  # Отметка задачи как выполненной
            task_id = input("Введите ID задачи для отметки как выполненной или нажмите Enter для отмены: ").strip()
            while task_id:
                if not task_id.isdigit():
                    print("Ошибка: ID должен быть числом.")
                else:
                    task_id = int(task_id)
                    task = manager.view_task_details(task_id)
                    if task:
                        clear_console()
                        if task.done:
                            print(f"Задача ID {task_id} уже выполнена.")
                        else:
                            manager.mark_task_done(task_id)
                            print(f"Задача ID {task_id} отмечена как выполненная.")
                    else:
                        print(f"Задача ID {task_id} не найдена.")
                task_id = input("Введите ID задачи для отметки как выполненной или нажмите Enter для отмены: ").strip()

        elif answer == '4':  # Редактирование задачи
            task_id = input("Введите ID задачи для редактирования или нажмите Enter для отмены: ").strip()
            clear_console()
            if not task_id:
                continue
            elif not task_id.isdigit():
                print("Ошибка: ID должен быть числом.")
            else:
                task_id = int(task_id)
                task = manager.view_task_details(task_id)
                if not task:
                    print(f"Задача ID {task_id} не найдена.")
                else:
                    new_title = input(
                        "Введите новое название задачи или нажмите Enter, чтобы оставить текущее: ").strip()
                    new_content = input(
                        "Введите новое описание задачи или нажмите Enter, чтобы оставить текущее: ").strip()

                    new_priority = input(
                        "Введите новый приоритет (Высокий/Средний/Низкий) или нажмите Enter, чтобы оставить текущий: ").capitalize()
                    while new_priority and new_priority not in ['Высокий', 'Средний', 'Низкий']:
                        print("Ошибка: приоритет должен быть 'Высокий', 'Средний' или 'Низкий'.")
                        new_priority = input(
                            "Введите новый приоритет или нажмите Enter, чтобы оставить текущий: ").capitalize()

                    new_due_time = input(
                        "Введите новую дату выполнения (ДД-ММ-ГГГГ) или нажмите Enter для сохранения текущей: ").strip()
                    while new_due_time:
                        try:
                            new_due_time = datetime.strptime(new_due_time, "%d-%m-%Y").strftime("%d-%m-%Y")
                            break
                        except ValueError:
                            print("Ошибка: неверный формат даты. Используйте ДД-ММ-ГГГГ.")
                            new_due_time = input(
                                "Введите новую дату выполнения (ДД-ММ-ГГГГ) или нажмите Enter для сохранения текущей: ").strip()

                    manager.edit_task(task_id, title=new_title, description=new_content, priority=new_priority,
                                      due_date=new_due_time)
                    clear_console()
                    print(f"Задача ID {task_id} успешно обновлена.")

        elif answer == '5':  # Удаление задачи
            task_id = input(
                "Введите ID задачи для удаления, ALL для удаления всех задач или нажмите Enter для отмены: ").strip()
            if task_id == "ALL":
                manager.delete_task("ALL")
                clear_console()
                print("Все задачи успешно удалены.")
            elif task_id.isdigit():
                clear_console()
                task_id = int(task_id)
                if manager.delete_task(task_id):
                    print(f"Задача ID {task_id} успешно удалена.")
                else:
                    print(f"Задача ID {task_id} не найдена.")
            else:
                print("Ошибка: ID должен быть числом или 'ALL'.")

        elif answer == '6':  # Экспорт задач в CSV
            export_path = input("Введите путь для сохранения файла: ").strip()
            manager.export_to_csv(export_path)
            print(f"Задачи успешно экспортированы в файл {export_path}.")

        elif answer == '7':  # Импорт задач из CSV
            import_path = input("Введите путь к CSV-файлу для импорта: ").strip()
            clear_console()
            if os.path.exists(import_path):
                manager.import_from_csv(import_path)
                print(f"Задачи успешно импортированы из файла {import_path}.")
            else:
                print(f'Файл {import_path} не существует')
        elif answer == '8':  # Выход из приложения
            print("Выход из приложения заметок..")
            break
        else:
            clear_console()
            print("Ошибка: выберите действие от 1 до 8.")


def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))


def validate_phone(phone):
    phone_regex = r'^(\+7|8)?[\s-]?(\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{2}[\s-]?\d{2}$'
    return bool(re.match(phone_regex, phone))


def contacts_app():
    manager = ContactManager()
    while True:
        print('1. Добавить новый контакт\n'
              '2. Просмотреть контакты\n'
              '3. Найти контакт\n'
              '4. Редактировать контакт\n'
              '5. Удалить контакт\n'
              '6. Экспорт контактов в CSV\n'
              '7. Импорт контактов из CSV\n'
              '8. Назад\n')
        answer = input('Выберите действие(1-8): ')
        clear_console()
        if answer == '1':
            name = input('Введите имя контакта: ')
            while not name:
                print('Поле имени обязательно должно быть заполнено')
                name = input('Введите имя контакта: ')
            phone = input('Введите номер телефона (или оставьте пустым): ')
            while phone:
                if validate_phone(phone):
                    break
                else:
                    print('Некорректный формат номера телефона.')
                    phone = input('Введите номер телефона (или оставьте пустым): ')
            email = input('Введите email (или оставьте пустым): ')
            while email:
                if validate_email(email):
                    break
                else:
                    print('Некорректный формат почты.')
                    email = input('Введите email (или оставьте пустым): ')

            manager.add_contact(name, phone, email)
            clear_console()
            print('Контакт успешно добавлен.\n')

        elif answer == '2':
            contacts = manager.contacts
            clear_console()
            if contacts:
                print("Список контактов:")
                for contact in contacts:
                    print(f"ID: {contact.id}, Имя: {contact.name}, Телефон: {contact.phone}, Email: {contact.email}")
            else:
                print('Список контактов пуст.\n')

        elif answer == '3':
            query = input('Введите имя или номер телефона для поиска: ')
            results = manager.search_contacts(query)
            clear_console()
            if results:
                print("Найденные контакты:")
                for contact in results:
                    print(f"ID: {contact.id}, Имя: {contact.name}, Телефон: {contact.phone}, Email: {contact.email}")
            else:
                print(f'Контакты по запросу "{query}" не найдены.\n')

        elif answer == '4':
            contact_id = input('Введите ID контакта, который хотите отредактировать, или Enter для отмены: ')
            if contact_id:
                try:
                    contact_id = int(contact_id)
                except ValueError:
                    print('Неверный формат ID.\n')
                    continue
                contact = manager.get_contact_by_id(contact_id)
                if contact is None:
                    print(f'Контакт с ID {contact_id} не найден.\n')
                else:
                    new_name = input('Введите новое имя или нажмите Enter, чтобы оставить прежнее: ')
                    new_phone = input('Введите новый номер телефона или нажмите Enter, чтобы оставить прежний: ')
                    new_email = input('Введите новый email или нажмите Enter, чтобы оставить прежний: ')
                    manager.edit_contact(contact_id, name=new_name, phone=new_phone, email=new_email)
                    print('Контакт успешно обновлён.\n')

        elif answer == '5':
            contact_id = input(
                'Введите ID контакта, который нужно удалить, ALL, чтобы удалить все или Enter для выхода: ')
            if contact_id:
                clear_console()
                if contact_id == 'ALL':
                    manager.delete_contact(contact_id)
                    print(f'Все контакты успешно удалены\n')
                else:
                    try:
                        contact_id = int(contact_id)
                    except ValueError:
                        print('Неверный формат ID.\n')
                        continue
                    if manager.get_contact_by_id(contact_id):
                        manager.delete_contact(contact_id)
                        print(f'Контакт с ID {contact_id} успешно удалён.\n')
                    else:
                        print(f'Контакт с ID {contact_id} не найден.\n')
        elif answer == '6':
            export_path = input('Введите путь к файлу для экспортирования: ')
            manager.export_to_csv(export_path)
            clear_console()
            print(f'Контакты успешно экспортированы в {export_path}.\n')

        elif answer == '7':
            import_path = input('Введите путь к файлу для импортирования: ')
            manager.import_from_csv(import_path)
            clear_console()
            print(f'Контакты успешно импортированы из {import_path}.\n')

        elif answer == '8':
            break

        else:
            print('Неправильный формат ввода. Введите число от 1 до 8.\n')


def format_number(number):
    return '{:,}'.format(round(number, 2)).replace(',', ' ')


def finance_app():
    manager = FinanceManager()

    while True:
        print("\nУправление финансовыми записями:\n"
              "1. Добавить новую запись\n"
              "2. Просмотреть записи\n"
              "3. Генерация отчёта\n"
              "4. Подсчет общего баланса\n"
              "5. Удалить запись\n"
              "6. Экспорт записей в CSV\n"
              "7. Импорт записей из CSV\n"
              "8. Выход\n")

        answer = input("Выберите действие: ")
        clear_console()
        if answer == "1":
            amount = input("Введите сумму операции (положительная для дохода, отрицательная для расхода): ")
            while True:
                try:
                    amount = float(amount)
                    break
                except ValueError:
                    print('Ошибка. Строка пустая или содержит ошибки')
                    amount = input("Введите сумму операции (положительная для дохода, отрицательная для расхода): ")
            category = input("Введите категорию операции(Например Еда, Транспорт и прочее: ").capitalize()
            date = input("Введите дату операции (в формате ДД-ММ-ГГГГ): ")
            while True:
                try:
                    date = datetime.strptime(date, "%d-%m-%Y").strftime("%d-%m-%Y")
                    break
                except ValueError:
                    print("Ошибка: неверный формат даты. Используйте ДД-ММ-ГГГГ.")
                    date = input("Введите срок выполнения (ДД-ММ-ГГГГ): ").strip()
            description = input("Введите описание операции: ")
            manager.add_record(amount, category, date, description)
            clear_console()
            print("Запись успешно добавлена.")

        elif answer == "2":
            print('Вывод по категориям?')
            category_filter = [i.lower() for i in
                               input("Напишите нужные категории или оставьте поле пустым для общего вывода: ").split()]
            records = manager.list_records(category=category_filter)
            clear_console()
            if records:
                print("\nСписок записей:")
                for record in records:
                    print(
                        f"ID: {record.id}, Сумма: {record.amount}, Категория: {record.category}, Дата: {record.date}, Описание: {record.description}")
            else:
                print("Записи не найдены.")

        elif answer == "3":
            start_date = input("Введите начальную дату (ДД-ММ-ГГГГ): ")
            while True:
                try:
                    start_date = datetime.strptime(start_date, "%d-%m-%Y").strftime("%d-%m-%Y")
                    break
                except ValueError:
                    print("Ошибка: неверный формат даты. Используйте ДД-ММ-ГГГГ.")
                    start_date = input("Введите начальную дату (ДД-ММ-ГГГГ): ")

            end_date = input("Введите конечную дату (ДД-ММ-ГГГГ): ")
            while True:
                try:
                    end_date = datetime.strptime(end_date, "%d-%m-%Y").strftime("%d-%m-%Y")
                    break
                except ValueError:
                    print("Ошибка: неверный формат даты. Используйте ДД-ММ-ГГГГ.")
                    end_date = input("Введите конечную дату (ДД-ММ-ГГГГ): ")
            clear_console()
            manager.generate_report(start_date, end_date)

        elif answer == "4":
            print(f'Общий баланс за все время: {format_number(manager.calculate_balance())}')
        elif answer == "5":
            record_id = input(
                'Введите ID записи, которую нужно удалить, ALL, чтобы удалить все записи или Enter для выхода: ')
            if record_id:
                clear_console()
                if record_id == 'ALL':
                    manager.delete_record(record_id)
                    print(f'Все записи успешно удалены\n')
                else:
                    try:
                        record_id = int(record_id)
                    except ValueError:
                        print('Неверный формат ID.\n')
                        continue
                    if manager.get_record_by_id(record_id):
                        manager.delete_record(record_id)
                        print(f'Запись с ID {record_id} успешно удалён.\n')
                    else:
                        print(f'Запись с ID {record_id} не найден.\n')

        elif answer == "6":
            export_path = input("Введите путь для сохранения CSV-файла: ")
            manager.export_to_csv(export_path)
            clear_console()
            print(f"Записи успешно экспортированы в {export_path}.\n")

        elif answer == "7":
            import_path = input("Введите путь к CSV-файлу для импорта: ")
            manager.import_from_csv(import_path)
            clear_console()
            print("Записи успешно импортированы.\n")

        elif answer == "8":
            print("Выход из приложения.")
            break

        else:
            print("Ошибка: Неверный выбор. Попробуйте снова.")


def check_values(x):
    if '**' in x:
        print('В выражении обнаружена попытка возведения в степень')
        return True
    for operator in '+-/*':
        x = x.replace(operator, ' ')
    len_of_numbers = [len(i) for i in x.split()]
    if max(len_of_numbers) > 9:
        print('Слишком большое значение. Число не должно превышать 10^9')
        return True
    if len(len_of_numbers) > 5:
        print('Слишком много значений. Не вводите больше 4 операторов в одном выражении')
        return True
    return False


def calculator():
    print('Добро пожаловать в калькулятор')
    print(
        '+ --> сложить,\n'
        '- --> Вычесть,\n'
        '* --> Умножить,\n'
        '/ -->  Разделить,\n'
    )
    while True:
        s = input('Введите математическое выражение или Enter для выхода: \n')
        if not s:
            break
        elif any(i not in '0123456789*/+-' for i in s):
            print('В выражении обнаружен неизвестный символ')
        elif check_values(s):
            continue
        else:
            try:
                print(f'= {eval(s)}')
            except ZeroDivisionError:
                print('Деление на ноль не разрешено.')
            except SyntaxError:
                print('Выражение записано неверно')


def main():
    print('Добро пожаловать в Персональный помощник!')
    while True:
        print('Выберите действие:\n'
              '1. Управление заметками\n'
              '2. Управление задачами\n'
              '3. Управление контактами\n'
              '4. Управление финансовыми записями\n'
              '5. Калькулятор\n'
              '6. Выход\n')
        answer = input('Выберите действие: ')
        clear_console()
        if answer == '1':
            note_app()
        elif answer == '2':
            task_app()
        elif answer == '3':
            contacts_app()
        elif answer == '4':
            finance_app()
        elif answer == '5':
            calculator()
        elif answer == '6':
            break
        else:
            print('Неправильный формат ввода. Введите число от 1 до 6\n')


# Пример использования
if __name__ == "__main__":
    main()

