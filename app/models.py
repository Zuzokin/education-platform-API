import re
import random
from app import USERS, EXPRS, QUEST
from abc import ABC, abstractmethod


class User:
    def __init__(self, user_id, first_name, last_name, phone, email, score=0):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.email = email
        self.score = score
        self.history = []

    def __str__(self):
        return f"({self.user_id}) {self.first_name} {self.last_name}"

    def __lt__(self, other):
        return self.score < other.score

    @staticmethod
    def is_valid_email(email):
        return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email)

    @staticmethod
    def is_valid_phone(phone):
        return re.fullmatch(
            r"^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$",
            phone,
        )

    @staticmethod
    def is_valid_id(user_id):
        return user_id in USERS.keys()

    def increase_score(self, amount=1):
        self.score += amount

    def solve(self, task, user_answer):
        if not isinstance(task, Question) and not isinstance(task, Expression):
            return None

        question = task
        result = question.to_dict()
        result["user_answer"] = user_answer
        result["reward"] = question.reward if user_answer == question.answer else 0
        self.history.append(result)

    def to_dict(self):
        return dict(
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "score": self.score,
            }
        )

    @staticmethod
    def get_leaderboard():
        return [user.to_dict() for user in sorted(USERS.values(), reverse=True)]


class Expression:
    def __init__(
        self, expr_id, operation, min_number, max_number, count_nums, reward=None
    ):
        self.expr_id = expr_id
        self.operation = operation
        self.values = [
            random.randint(min_number, max_number) for _ in range(count_nums)
        ]
        self.answer = self.__evaluate()
        if reward is None:
            reward = len(self.values) - 1
        self.reward = reward

    def __str__(self):
        return f"({self.expr_id}) {self.to_string()} = {self.answer}"

    @staticmethod
    def is_valid_id(expr_id):
        return expr_id in EXPRS.keys()

    def __evaluate(self):
        return eval(self.to_string())

    def to_string(self):
        expr_str = str(self.values[0]) + "".join(
            f" {self.operation} {value}" for value in self.values[1:]
        )
        return expr_str

    def to_dict(self):
        return dict(
            {
                "id": self.expr_id,
                "operation": self.operation,
                "values": self.values,
                "string_expression": self.to_string(),
            }
        )


class Question(ABC):
    def __init__(self, question_id, title, description, reward=1):
        self.question_id = question_id
        self.title = title
        self.description = description
        self.reward = reward
        self._answer = None

    @property
    @abstractmethod
    def answer(self):
        return self._answer

    def __str__(self):
        return f"({self.question_id}) {self.title}"

    @staticmethod
    def is_valid_id(question_id):
        return question_id in QUEST.keys()


class OneAnswer(Question):
    def __init__(self, question_id, title, description, answer: str, reward=1):
        super().__init__(question_id, title, description, reward)
        if self.is_valid(answer):
            self._answer = answer
        else:
            self._answer = None

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, value: str):
        if self.is_valid(value):
            self._answer = value

    @staticmethod
    def is_valid(answer):
        return isinstance(answer, str)

    def to_dict(self):
        return dict(
            {
                "id": self.question_id,
                "title": self.title,
                "description": self.description,
                "type": "ONE-ANSWER",
                "answer": self._answer,
            }
        )


class MultipleChoice(Question):
    def __init__(
        self, question_id, title, description, answer: int, choices: list, reward=1
    ):
        super().__init__(question_id, title, description, reward)
        if self.is_valid(answer, choices):
            self._answer = answer
            self.choices = choices
        else:
            self._answer = None
            self.choices = None

    @property
    def answer(self):
        return self._answer

    @answer.setter
    def answer(self, value: int):
        if self.is_valid(value, self.choices):
            self._answer = value

    @staticmethod
    def is_valid(answer, choices):
        if not isinstance(answer, int) or not isinstance(choices, list):
            return False
        if answer < 0 or answer >= len(choices):
            return False
        return True

    def to_dict(self):
        return dict(
            {
                "id": self.question_id,
                "title": self.title,
                "description": self.description,
                "type": "MULTIPLE-CHOICE",
                "choices": self.choices,
                "answer": self._answer,
            }
        )
