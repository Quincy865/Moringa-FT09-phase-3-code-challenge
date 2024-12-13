import sys
sys.path.append('/Users/qsnotfound/Development/code/phase-3/Moringa-FT09-phase-3-code-challenge')
from database.connection import get_db_connection


class Author:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

        if id is None and name is not None:
            self._insert_into_db()

    def __repr__(self):
        return f'<Author {self.name}>'

    def _insert_into_db(self):
        """Insert the author into the database."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO authors (name) VALUES (?)
                ''', (self.name,))
                conn.commit()
                self.id = cursor.lastrowid  
        except Exception as e:
            print(f"Error inserting author into DB: {e}")

    # Getter and Setter for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._name = value
        else:
            raise ValueError("Name must be a non-empty string.")

    def articles(self):
        """Fetch all articles written by this author."""
        try:
            from .article import Article  # Import inside the function to avoid circular imports
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM articles WHERE author_id = ?
                ''', (self.id,))
                rows = cursor.fetchall()
                # Return a list of Article objects for the fetched rows
                return [Article(id=row['id'], title=row['title'], content=row['content'],
                                author=self, magazine=row['magazine_id']) for row in rows]
        except Exception as e:
            print(f"Error fetching articles for author {self.id}: {e}")
            return []

    def magazines(self):
        """Fetch all magazines this author has written for."""
        try:
            from .magazine import Magazine  # Import inside the function to avoid circular imports
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DISTINCT magazines.* FROM magazines
                    JOIN articles ON magazines.id = articles.magazine_id
                    WHERE articles.author_id = ?
                ''', (self.id,))
                rows = cursor.fetchall()
                # Return a list of Magazine objects for the fetched rows
                return [Magazine(id=row['id'], name=row['name'], category=row['category']) for row in rows]
        except Exception as e:
            print(f"Error fetching magazines for author {self.id}: {e}")
            return []

    @staticmethod
    def get_by_id(author_id):
        """Fetch an author by ID."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM authors WHERE id = ?', (author_id,))
                row = cursor.fetchone()
                if row:
                    return Author(id=row['id'], name=row['name'])
                return None
        except Exception as e:
            print(f"Error fetching author by ID {author_id}: {e}")
            return None
