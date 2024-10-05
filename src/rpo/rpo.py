import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional


class ResearchPaperOrganizer:
    def __init__(self, db_path: str, pdf_dir: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.pdf_dir = Path(pdf_dir)
        self.setup_database()

    def setup_database(self) -> None:
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY,
                title TEXT,
                year INTEGER,
                file_path TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_authors (
                paper_id INTEGER,
                author_id INTEGER,
                FOREIGN KEY (paper_id) REFERENCES papers (id),
                FOREIGN KEY (author_id) REFERENCES authors (id)
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY,
                keyword TEXT
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS paper_keywords (
                paper_id INTEGER,
                keyword_id INTEGER,
                FOREIGN KEY (paper_id) REFERENCES papers (id),
                FOREIGN KEY (keyword_id) REFERENCES keywords (id)
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bibtex_entries (
                paper_id INTEGER,
                bibtex TEXT,
                FOREIGN KEY (paper_id) REFERENCES papers (id)
            )
        """
        )
        self.conn.commit()

    def add_paper(
        self,
        title: str,
        year: int,
        authors: List[str],
        keywords: List[str],
        bibtex: str,
        file_path: str,
    ) -> None:
        # Add paper
        self.cursor.execute(
            "INSERT INTO papers (title, year, file_path) VALUES (?, ?, ?)",
            (title, year, str(file_path)),
        )
        paper_id = self.cursor.lastrowid

        # Add authors
        for author in authors:
            self.cursor.execute(
                "INSERT OR IGNORE INTO authors (name) VALUES (?)", (author,)
            )
            self.cursor.execute("SELECT id FROM authors WHERE name = ?", (author,))
            author_id = self.cursor.fetchone()[0]
            self.cursor.execute(
                "INSERT INTO paper_authors (paper_id, author_id) VALUES (?, ?)",
                (paper_id, author_id),
            )

        # Add keywords
        for keyword in keywords:
            self.cursor.execute(
                "INSERT OR IGNORE INTO keywords (keyword) VALUES (?)", (keyword,)
            )
            self.cursor.execute("SELECT id FROM keywords WHERE keyword = ?", (keyword,))
            keyword_id = self.cursor.fetchone()[0]
            self.cursor.execute(
                "INSERT INTO paper_keywords (paper_id, keyword_id) VALUES (?, ?)",
                (paper_id, keyword_id),
            )

        # Add bibtex
        self.cursor.execute(
            "INSERT INTO bibtex_entries (paper_id, bibtex) VALUES (?, ?)",
            (paper_id, bibtex),
        )

        self.conn.commit()

    def search_papers(self, query: str) -> List[Tuple[str, int, str]]:
        self.cursor.execute(
            """
            SELECT DISTINCT p.title, p.year, p.file_path
            FROM papers p
            LEFT JOIN paper_authors pa ON p.id = pa.paper_id
            LEFT JOIN authors a ON pa.author_id = a.id
            LEFT JOIN paper_keywords pk ON p.id = pk.paper_id
            LEFT JOIN keywords k ON pk.keyword_id = k.id
            WHERE p.title LIKE ? OR a.name LIKE ? OR k.keyword LIKE ?
        """,
            ("%" + query + "%", "%" + query + "%", "%" + query + "%"),
        )
        return self.cursor.fetchall()

    def get_paper_details(
        self, paper_id: int
    ) -> Optional[Tuple[str, int, str, str, str, str]]:
        self.cursor.execute(
            """
            SELECT p.title, p.year, p.file_path, GROUP_CONCAT(DISTINCT a.name), 
                   GROUP_CONCAT(DISTINCT k.keyword), b.bibtex
            FROM papers p
            LEFT JOIN paper_authors pa ON p.id = pa.paper_id
            LEFT JOIN authors a ON pa.author_id = a.id
            LEFT JOIN paper_keywords pk ON p.id = pk.paper_id
            LEFT JOIN keywords k ON pk.keyword_id = k.id
            LEFT JOIN bibtex_entries b ON p.id = b.paper_id
            WHERE p.id = ?
            GROUP BY p.id
        """,
            (paper_id,),
        )
        return self.cursor.fetchone()

    def list_all_papers(self) -> List[Tuple[int, str, int]]:
        self.cursor.execute(
            """
            SELECT p.id, p.title, p.year
            FROM papers p
            ORDER BY p.year DESC, p.title
        """
        )
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
