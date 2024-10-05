# Research Paper Organiser

Research Paper Organiser is a command-line tool designed to help researchers and students manage their collection of academic papers. It allows you to store, organize, and quickly retrieve information about your research papers, including metadata, keywords, and BibTeX entries.

## Features

- Add new papers with metadata (title, year, authors, keywords)
- Store BibTeX entries for easy citation
- Search papers by title, author, or keyword
- List all papers in the database
- View detailed information about specific papers

## Installation

1. Ensure you have Python 3.7 or higher installed.

2. Clone this repository:
   ```
   git clone https://github.com/blake-armstrong/RPO.git
   cd RPO
   ```

3. Install the package:
   ```
   pip install -e .
   ```

## Usage

After installation, you can use the `rpo` command to interact with the tool. Here are the available commands:

### Add a new paper

```
rpo add --title "Paper Title" --year 2023 --authors "Author One" "Author Two" --keywords "keyword1" "keyword2" --bibtex "@article{...}" --file "path/to/paper.pdf"
```

### Search for papers

```
rpo search "query"
```

This will search for the query in titles, authors, and keywords.

### List all papers

```
rpo list
```

### View paper details

```
rpo details <paper_id>
```

Replace `<paper_id>` with the ID of the paper you want to view.

### Get help

For help with any command, add `--help` after the command:

```
rpo --help
rpo add --help
```

## Configuration

By default, the program uses a SQLite database named `research_papers.db` in the current directory and expects PDF files to be stored in `~/research_papers/`. You can change these defaults by using the `--db` and `--pdf_dir` options:

```
rpo --db /path/to/database.db --pdf_dir /path/to/pdf/directory [command]
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
