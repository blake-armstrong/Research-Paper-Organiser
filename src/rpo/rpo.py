import sqlite3
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
import subprocess
import platform
import os
import textwrap
import bibtexparser

from .config import Config


@dataclass
class Paper:
    id: int
    authors: str
    year: int
    journal: str
    title: str
    file_path: str


class ResearchPaperOrganiser:
    def __init__(self, config: Config):
        self.conn: sqlite3.Connection = sqlite3.connect(config.db_path)
        self.cursor: sqlite3.Cursor = self.conn.cursor()
        # self.pdf_dir: Path = Path(pdf_dir)
        self.setup_database()
        self.update_database_schema()

    def setup_database(self) -> None:
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                year INTEGER,
                file_path TEXT,
                journal TEXT
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

    def parse_bibtex(self, bibtex: str) -> Dict[str, str]:
        bib_database = bibtexparser.loads(bibtex)
        if not bib_database.entries:
            raise ValueError("Invalid BibTeX entry")
        return bib_database.entries[0]

    def add_paper(self, bibtex: str, file_path: str, keywords: List[str]) -> None:
        # Check for duplicate BibTeX entry
        self.cursor.execute(
            "SELECT COUNT(*) FROM bibtex_entries WHERE bibtex = ?", (bibtex,)
        )
        if self.cursor.fetchone()[0] > 0:
            raise ValueError(
                "A paper with this BibTeX entry already exists in the database."
            )

        bib_data = self.parse_bibtex(bibtex)

        title = bib_data.get("title", "")
        year = int(bib_data.get("year", 0))
        authors = [
            author.strip() for author in bib_data.get("author", "").split(" and ")
        ]
        journal = bib_data.get("journal", "")

        # Add paper
        self.cursor.execute(
            "INSERT INTO papers (title, year, file_path, journal) VALUES (?, ?, ?, ?)",
            (title, year, str(file_path), journal),
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

    def remove_paper(self, paper_id: int) -> None:
        # Start a transaction
        self.conn.execute("BEGIN TRANSACTION")
        try:
            # Check if paper exists
            self.cursor.execute("SELECT COUNT(*) FROM papers WHERE id = ?", (paper_id,))
            if self.cursor.fetchone()[0] == 0:
                raise ValueError(f"No paper found with ID {paper_id}")

            # Remove paper and related entries
            self.cursor.execute("DELETE FROM papers WHERE id = ?", (paper_id,))
            self.cursor.execute(
                "DELETE FROM paper_authors WHERE paper_id = ?", (paper_id,)
            )
            self.cursor.execute(
                "DELETE FROM paper_keywords WHERE paper_id = ?", (paper_id,)
            )
            self.cursor.execute(
                "DELETE FROM bibtex_entries WHERE paper_id = ?", (paper_id,)
            )

            # Get all papers with id greater than the removed paper
            self.cursor.execute(
                "SELECT id FROM papers WHERE id > ? ORDER BY id", (paper_id,)
            )
            papers_to_update = self.cursor.fetchall()

            # Update paper ids and related entries
            for (old_id,) in papers_to_update:
                new_id = old_id - 1

                # Update papers table
                self.cursor.execute(
                    "UPDATE papers SET id = ? WHERE id = ?", (new_id, old_id)
                )

                # Update paper_authors table
                self.cursor.execute(
                    "UPDATE paper_authors SET paper_id = ? WHERE paper_id = ?",
                    (new_id, old_id),
                )

                # Update paper_keywords table
                self.cursor.execute(
                    "UPDATE paper_keywords SET paper_id = ? WHERE paper_id = ?",
                    (new_id, old_id),
                )

                # Update bibtex_entries table
                self.cursor.execute(
                    "UPDATE bibtex_entries SET paper_id = ? WHERE paper_id = ?",
                    (new_id, old_id),
                )

            # Reset the auto-increment counter
            self.cursor.execute(
                "UPDATE sqlite_sequence SET seq = (SELECT MAX(id) FROM papers) WHERE name = 'papers'"
            )

            # Commit the transaction
            self.conn.commit()
            print(
                f"Paper with ID {paper_id} removed and remaining paper IDs reordered."
            )

        except Exception as e:
            # If any error occurs, roll back the transaction
            self.conn.rollback()
            print(f"An error occurred: {e}")
            raise

    def get_paper_details(self, paper_id: int) -> Optional[Paper]:
        self.cursor.execute(
            """
            SELECT p.title, p.year, p.file_path, p.journal, GROUP_CONCAT(DISTINCT a.name), 
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

    def update_database_schema(self) -> None:
        try:
            self.cursor.execute("SELECT journal FROM papers LIMIT 1")
        except sqlite3.OperationalError:
            # Journal column doesn't exist, so add it
            self.cursor.execute("ALTER TABLE papers ADD COLUMN journal TEXT")
            self.conn.commit()
            print("Database schema updated to include 'journal' column.")

    def get_paper_file_path(self, paper_id: int) -> Optional[str]:
        self.cursor.execute("SELECT file_path FROM papers WHERE id = ?", (paper_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def open_paper(self, paper_id: int) -> None:
        file_path = self.get_paper_file_path(paper_id)
        if not file_path:
            print(f"No paper found with ID {paper_id}")
            return

        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.call(("open", file_path))
            elif platform.system() == "Windows":  # Windows
                os.startfile(file_path)
            else:  # linux variants
                subprocess.call(("xdg-open", file_path))
            print(f"Opened file: {file_path}")
        except Exception as e:
            print(f"Error opening file: {e}")

    def format_authors(self, authors: str) -> str:
        author_list = authors.split(" and ")
        if len(author_list) > 2:
            return f"{author_list[0]} et al."
        return " & ".join(author_list)

    def list_all_papers(self) -> List[Paper]:
        self.cursor.execute(
            """
            SELECT p.id, 
                   GROUP_CONCAT(a.name, ' and ') as authors,
                   p.year, 
                   p.journal, 
                   p.title,
                   p.file_path
            FROM papers p
            LEFT JOIN paper_authors pa ON p.id = pa.paper_id
            LEFT JOIN authors a ON pa.author_id = a.id
            GROUP BY p.id
            ORDER BY p.year DESC, p.title
            """
        )
        papers = self.cursor.fetchall()
        return [
            Paper(id, self.format_authors(authors), year, journal, title, file_path)
            for id, authors, year, journal, title, file_path in papers
        ]

    def print_papers(self, papers: List[Paper]) -> None:
        if not papers:
            print("No papers found.")
            return

        # Define column widths
        id_width = 4
        authors_width = 30
        year_width = 6
        journal_width = 20
        title_width = 50

        # Print header
        print(
            f"{'ID':<{id_width}} {'Authors':<{authors_width}} {'Year':<{year_width}} {'Journal':<{journal_width}} {'Title'}"
        )
        print(
            "-"
            * (4 + id_width + authors_width + year_width + journal_width + title_width)
        )

        # Print each paper
        for paper in papers:
            # Truncate authors if too long
            authors = paper.authors
            if len(authors) > authors_width:
                authors = authors[: authors_width - 3] + "..."

            # Truncate journal if too long
            journal = paper.journal
            if len(journal) > journal_width:
                journal = journal[: journal_width - 3] + "..."

            # Wrap title
            wrapped_title = textwrap.wrap(paper.title, width=title_width)

            # Print first line
            print(
                f"{paper.id:<{id_width}} {authors:<{authors_width}} {paper.year:<{year_width}} {journal:<{journal_width}} {wrapped_title[0]}"
            )

            # Print remaining lines of title, if any
            for line in wrapped_title[1:]:
                print(
                    f"{'':<{id_width}} {'':<{authors_width}} {'':<{year_width}} {'':<{journal_width}} {line}"
                )

            print()  # Add a blank line between papers

    def search_papers(self, query: str) -> List[Paper]:
        self.cursor.execute(
            """
            SELECT p.id, 
                   GROUP_CONCAT(a.name, ' and ') as authors,
                   p.year, 
                   p.journal, 
                   p.title,
                   p.file_path
            FROM papers p
            LEFT JOIN paper_authors pa ON p.id = pa.paper_id
            LEFT JOIN authors a ON pa.author_id = a.id
            LEFT JOIN paper_keywords pk ON p.id = pk.paper_id
            LEFT JOIN keywords k ON pk.keyword_id = k.id
            WHERE p.title LIKE ? OR a.name LIKE ? OR k.keyword LIKE ?
            GROUP BY p.id
            ORDER BY p.year DESC, p.title
            """,
            ("%" + query + "%", "%" + query + "%", "%" + query + "%"),
        )
        papers = self.cursor.fetchall()
        return [
            Paper(id, self.format_authors(authors), year, journal, title, file_path)
            for id, authors, year, journal, title, file_path in papers
        ]

    def close(self):
        self.conn.close()
