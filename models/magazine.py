import sys
sys.path.append('/Users/qsnotfound/Development/code/phase-3/Moringa-FT09-phase-3-code-challenge')
from database.connection import get_db_connection


class Magazine:
    def __init__(self, id=None, name=None, category=None):
        self.id = id
        self.name = name
        self.category = category

        if id is None and name is not None and category is not None:
            self._insert_into_db()

    def __repr__(self):
        return f'<Magazine {self.name}>'

    def _insert_into_db(self):
        """Insert the magazine into the database."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO magazines (name, category) VALUES (?, ?)
                ''', (self.name, self.category))
                conn.commit()
                self.id = cursor.lastrowid 
        except Exception as e:
            print(f"Error inserting magazine into DB: {e}")

    # Getter and Setter for name
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if isinstance(value, str) and 2 <= len(value) <= 16:
            self._name = value
        else:
            raise ValueError("Name must be a string between 2 and 16 characters.")

    # Getter and Setter for category
    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._category = value
        else:
            raise ValueError("Category must be a non-empty string.")

    def articles(self):
        """Fetch all articles published in this magazine."""
        try:
            from .article import Article  # Import inside the function to avoid circular imports
            from .author import Author  # Import inside the function to avoid circular imports

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM articles WHERE magazine_id = ?
                ''', (self.id,))
                rows = cursor.fetchall()
                # Return a list of Article objects for the fetched rows
                return [Article(id=row['id'], title=row['title'], content=row['content'],
                                author=Author.get_by_id(row['author_id']), magazine=self) for row in rows]
        except Exception as e:
            print(f"Error fetching articles for magazine {self.id}: {e}")
            return []

    def contributors(self):
        """Fetch all authors who have contributed to this magazine."""
        try:
            from .author import Author  # Import inside the function to avoid circular imports
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DISTINCT authors.* FROM authors
                    JOIN articles ON authors.id = articles.author_id
                    WHERE articles.magazine_id = ?
                ''', (self.id,))
                rows = cursor.fetchall()
                # Return a list of Author objects for the fetched rows
                return [Author(id=row['id'], name=row['name']) for row in rows]
        except Exception as e:
            print(f"Error fetching contributors for magazine {self.id}: {e}")
            return []

    def article_titles(self):
        """Fetch all article titles published in this magazine."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT title FROM articles WHERE magazine_id = ?
                ''', (self.id,))
                rows = cursor.fetchall()
                return [row['title'] for row in rows] if rows else None
        except Exception as e:
            print(f"Error fetching article titles for magazine {self.id}: {e}")
            return None

    def contributing_authors(self):
        """Fetch authors who have contributed more than 2 articles to this magazine."""
        try:
            from .author import Author  # Import inside the function to avoid circular imports

            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT authors.* FROM authors
                    JOIN articles ON authors.id = articles.author_id
                    WHERE articles.magazine_id = ?
                    GROUP BY authors.id
                    HAVING COUNT(articles.id) > 2
                ''', (self.id,))
                rows = cursor.fetchall()
                # Return a list of Author objects for the fetched rows
                return [Author(id=row['id'], name=row['name']) for row in rows] if rows else None
        except Exception as e:
            print(f"Error fetching contributing authors for magazine {self.id}: {e}")
            return None

    @staticmethod
    def get_by_id(magazine_id):
        """Fetch a magazine by its ID."""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM magazines WHERE id = ?', (magazine_id,))
                row = cursor.fetchone()
                if row:
                    return Magazine(id=row['id'], name=row['name'], category=row['category'])
                return None
        except Exception as e:
            print(f"Error fetching magazine by ID {magazine_id}: {e}")
            return None
