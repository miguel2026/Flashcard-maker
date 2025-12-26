from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field
import pytz


@dataclass
class User:
    name: str
    email: str
    age: Optional[int] = None

    chats: List["Chat"] = field(default_factory=list)
    decks: List["Deck"] = field(default_factory=list)
    exercise_sets: List["ExerciseSet"] = field(default_factory=list)

    id: Optional[int] = None

@dataclass
class Chat:
    user_id: Optional[int] = None
    topic: str = "..."
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Sao_Paulo"))
    )

    iterations: List["Iteration"] = field(default_factory=list)

    id: Optional[int] = None

    def put_iteration(self, message: str, response: str = ''):
        self.iterations.append(
            Iteration(
                id=None,
                chat_id=self.id,
                message=message,
                response=response
            )
        )

    def change_ids_iterations(self):
        for iteration in self.iterations:
            iteration.chat_id = self.id
    def get_iterations(self):

        iterations = []
        
        for iteration in self.iterations:
            iteration = iteration.get_iteration()

            if iteration is None:
                raise TypeError("Iteration cannot be None")

            for message in iteration:
                iterations.append(message)

        return iterations

@dataclass
class Iteration:
    message: Optional[str] = None
    response: Optional[str] = None

    def get_iteration(self) -> List[dict[str, str]]:
        iteration = []
        
        if self.message != None:
            iteration.append({"role": "user", "content": self.message})
        
        if self.response != None:
            iteration.append({"role": "assistant", "content": self.response})

        if len(iteration) > 0:
            return iteration
        else:
            raise ValueError('Iteration is empty')

    def get_prompt(self) -> dict:
        return {"role": "user", "content": self.message}

    def get_output(self)  -> dict:
        return {"role": "assistant", "content": self.response}
    
    id: Optional[int] = None
    chat_id: Optional[int] = None

@dataclass
class Deck:
    user_id: int
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Sao_Paulo"))
    )
    flashcards: List["Flashcard"] = field(default_factory=list)
    id: Optional[int] = None

@dataclass
class Flashcard:
    deck_id: int
    question: str
    answer: str
    image_path_question: Optional[str] = None
    image_path_answer: Optional[str] = None
    id: Optional[int] = None

@dataclass
class ExerciseSet:
    user_id: int
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(pytz.timezone("America/Sao_Paulo"))
    )
    exercises: List["Exercise"] = field(default_factory=list)
    id: Optional[int] = None

@dataclass
class Exercise:
    exercise_set_id: int
    question: str
    answer: str
    image_path_question: Optional[str] = None
    image_path_answer: Optional[str] = None
    id: Optional[int] = None