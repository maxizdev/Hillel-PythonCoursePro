from abc import abstractmethod, ABC
from pydantic import BaseModel
from datetime import datetime
from typing import List, Generator


class BookModel(BaseModel):
    title: str
    author: str
    year: int


class Publication(ABC):
    def __init__(self, book_model: BookModel):
        self._title = book_model.title
        self._author = book_model.author
        self._year = book_model.year

    @property
    def title(self):
        return self._title

    @property
    def author(self):
        return self._author

    @property
    def year(self):
        return self._year

    @abstractmethod
    def __str__(self) -> str:
        pass

    @property
    @abstractmethod
    def publication_type(self):
        pass


class Book(Publication):
    def __str__(self) -> str:
        return f'{self.title} - {self.author}, {self.year}'

    @property
    def publication_type(self):
        return "book"


def adding_log(func):
    def wrapper(self, publication: Publication, *args, **kwargs):
        res = func(self, publication, *args, **kwargs)
        print(f'Added publication {publication} at {datetime.now()}.')
        return res
    return wrapper

def find_publication(func):
    def wrapper(self, publication: Publication, *args, **kwargs):
        if publication in self.publications:
            return func(self, publication, *args, **kwargs)
        print(f'Publication "{publication}" not found.')
        return None
    return wrapper


class Library:
    def __init__(self, publications_list: List[Publication]):
        self.__publications = publications_list

    @property
    def publications(self):
        return self.__publications

    def __iter__(self):
        self._current_publication = 0
        return self

    def __next__(self):
        if self._current_publication >= len(self.__publications):
            raise StopIteration

        publication = self.__publications[self._current_publication]
        self._current_publication += 1
        return publication

    def publication_generator(self, author: str) -> Generator[Publication, None, None]:
        for publication in self.__publications:
            if publication.author == author:
                yield publication

    @adding_log
    def add_publication(self, publication: Publication) -> None:
        self.__publications.append(publication)

    @find_publication
    def remove_publication(self, publication: Publication) -> None:
        self.__publications.remove(publication)

    def __str__(self):
        content = '\n'.join(str(publication) for publication in self.__publications)
        return f'Library of {len(self.__publications)} publications:\n{content}'


class FileManager:
    def __init__(self, filename: str):
        self.filename = filename

    def load(self, library: Library):
        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    parts = line.strip().split(' | ')
                    if len(parts) != 4:
                        print(f'Incorrect line: {line.strip()}')
                        continue

                    title, author, year, publication_type = parts
                    model = BookModel(title=title, author=author, year=int(year))
                    if publication_type == 'book':
                        publication = Book(model)
                    elif publication_type == 'magazine':
                        publication = Magazine(model)
                    else:
                        continue
                    library.add_publication(publication)
            print(f'Imported publications from {self.filename}.')
        except FileNotFoundError:
            print(f'File "{self.filename}" not found.')

    def save(self, library: Library):
        with open(self.filename, 'w') as file:
            for publ in library.publications:
                file.write(f"{publ.title} | {publ.author} | {publ.year} | {publ.publication_type}\n")
        print(f'Library was saved to "{self.filename}".')


class Magazine(Book):
    def __str__(self):
        return f'[Magazine] {super().__str__()}'

    @property
    def publication_type(self):
        return "magazine"


# --- Тестування ---
if __name__ == "__main__":
    # 1. Створення бібліотеки
    library = Library([])

    # 2. Створення інстансу книги та журналу
    book1 = Book(BookModel(title="1984", author="George Orwell", year=1949))
    magazine1 = Magazine(BookModel(title="National Geographic", author="Various", year=2023))

    # 3. Додавання їх у бібліотеку
    library.add_publication(book1)
    library.add_publication(magazine1)

    # 4. Виведення списку книг у бібліотеці
    print("📚 Усі публікації:")
    print(library)

    # 5. Виведення списку книг бібліотеки по імені автора
    print("\n📚 Публікації George Orwell:")
    for pub in library.publication_generator("George Orwell"):
        print(pub)

    # 6. Збереження списку книг у файл
    fm = FileManager("library.txt")
    fm.save(library)

    # 7. Видалення книги з бібліотеки
    library.remove_publication(book1)

    # 8. Виведення списку книг після видалення
    print("\n📚 Після видалення:")
    print(library)

    # 9. Додавання книг з файлу в бібліотеку
    fm.load(library)  # У __enter__ відбудеться додавання

    # 10. Виведення списку книг бібліотеки після додавання
    print("\n📚 Після повторного додавання:")
    print(library)