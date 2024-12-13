import sys
sys.path.append('/Users/qsnotfound/Development/code/phase-3/Moringa-FT09-phase-3-code-challenge')
from database.connection import get_db_connection


class Article:
    def __init__(self, id=None, title=None, content=None, author=None, magazine=None):
        self.id = id
        self._title = title
        self._content = content
        self.author = author  # Author object or ID
        self.magazine = magazine  # Magazine object or ID

        if self.id is None:  # Insert into DB only if it's a new article
            self._insert_into_db()

    def __repr__(self):
        return f'<Article {self.title}>'

    def _insert_into_db(self):
        """Insert a new article into the database."""
        try:
            # Import Author and Magazine inside the function to avoid circular imports
            from .author import Author
            from .magazine import Magazine

            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Use author and magazine objects or IDs
                author_id = self.author.id if isinstance(self.author, Author) else self.author
                magazine_id = self.magazine.id if isinstance(self.magazine, Magazine) else self.magazine

                cursor.execute('''
                    INSERT INTO articles (title, content, author_id, magazine_id)
                    VALUES (?, ?, ?, ?)
                ''', (self.title, self.content, author_id, magazine_id))
                conn.commit()
                self.id = cursor.lastrowid  # Set the article ID after insertion
        except Exception as e:
            raise Exception(f"Error inserting article into DB: {e}")

    # Getter and Setter for title
    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        if isinstance(value, str) and 5 <= len(value) <= 50:
            self._title = value
        else:
            raise ValueError("Title must be a string between 5 and 50 characters.")

    # Getter and Setter for content
    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._content = value
        else:
            raise ValueError("Content must be a non-empty string.")

    def get_author(self):
        """Fetch the author of the article."""
        if isinstance(self.author, Author):
            return self.author
        # Fallback to fetching author from the database
        from .author import Author  # Import inside method to prevent circular import
        return Author.get_by_id(self.author)

    def get_magazine(self):
        """Fetch the magazine of the article."""
        if isinstance(self.magazine, Magazine):
            return self.magazine
        # Fallback to fetching magazine from the database
        from .magazine import Magazine  # Import inside method to prevent circular import
        return Magazine.get_by_id(self.magazine)

    @staticmethod
    def get_articles_by_author(author_id):
        """Fetch articles by the author ID."""
        try:
            from .author import Author  # Import inside the function to avoid circular imports
            from .magazine import Magazine  # Import inside the function to avoid circular imports

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM articles WHERE author_id = ?', (author_id,))
                rows = cursor.fetchall()
                # Create a list of Article objects
                return [Article(id=row['id'], title=row['title'], content=row['content'],
                                author=Author.get_by_id(row['author_id']), magazine=Magazine.get_by_id(row['magazine_id']))
                        for row in rows]
        except Exception as e:
            raise Exception(f"Error fetching articles by author: {e}")

    @staticmethod
    def get_by_id(article_id):
        """Fetch an article by ID."""
        try:
            from .author import Author  # Import inside method to prevent circular import
            from .magazine import Magazine  # Import inside method to prevent circular import

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
                row = cursor.fetchone()
                if row:
                    # Return an Article object
                    return Article(id=row['id'], title=row['title'], content=row['content'],
                                   author=Author.get_by_id(row['author_id']), magazine=Magazine.get_by_id(row['magazine_id']))
                return None  # Return None if the article is not found
        except Exception as e:
            raise Exception(f"Error fetching article by ID: {e}")
