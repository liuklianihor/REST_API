from app.models.book_model import books_db


def _find_index(book_id):
    target = str(book_id)
    for index, item in enumerate(books_db):
        if str(item["id"]) == target:
            return index
    return None


async def get_all_books():
    return list(books_db)


async def get_book_by_id(book_id):
    index = _find_index(book_id)
    if index is None:
        return None
    return books_db[index]


async def add_book(book):
    books_db.append(book)
    return book


async def delete_book(book_id):
    index = _find_index(book_id)
    if index is None:
        return False

    del books_db[index]
    return True
