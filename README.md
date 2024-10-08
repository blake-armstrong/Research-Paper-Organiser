# Research Paper Organiser (RPO)

Research Paper Organiser (RPO) is a command-line tool designed to help researchers manage their collection of academic papers. It allows you to add, search, list, and organize research papers along with their metadata and associated PDF files.

## Features

- Add papers with BibTeX information and PDF files
- Search papers by title, author, or keyword
- List all papers in the database
- View detailed information about a specific paper
- Open the PDF file associated with a paper
- Remove papers from the database
- Automatically reorder paper IDs to maintain consistency

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/blake-armstrong/Research-Paper-Organiser.git
   cd research-paper-organizer
   ```

2. Install the package:
   ```
   pip install .
   ```

## Configuration

Before using the program, you need to set up the configuration:

```
rpo config
```

You will be prompted to enter:
- The path for the database file
- The directory for storing PDF files

## Usage

After installation, you can use the `rpo` command to run the Research Paper Organiser.

### Adding a paper

```
rpo add --bibtex "bibtex_entry" --file "path/to/pdf" --keywords keyword1 keyword2
```

### Searching for papers

```
rpo search "query"
```

### Listing all papers

```
rpo list
```

### Viewing paper details

```
rpo details <paper_id>
```

### Opening a paper's PDF

```
rpo open <paper_id>
```

### Removing a paper

```
rpo remove <paper_id>
```

## File Structure

- `__main__.py`: The main entry point of the program
- `rpo.py`: Contains the `ResearchPaperOrganiser` class with core functionality
- `config.py`: Handles configuration management

## Dependencies

- bibtexparser: For parsing BibTeX entries
- sqlite3: For database management (included in Python standard library)
- subprocess, platform: For opening PDF files (included in Python standard library)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
