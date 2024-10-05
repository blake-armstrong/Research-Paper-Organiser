import argparse
from .rpo import ResearchPaperOrganizer


def main() -> None:
    parser = argparse.ArgumentParser(description="Research Paper Organizer")
    parser.add_argument(
        "--db", default="research_papers.db", help="Path to the SQLite database"
    )
    parser.add_argument(
        "--pdf_dir", default="~/research_papers/", help="Directory for PDF storage"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add paper
    add_parser = subparsers.add_parser("add", help="Add a new paper")
    add_parser.add_argument("--title", required=True, help="Paper title")
    add_parser.add_argument("--year", type=int, required=True, help="Publication year")
    add_parser.add_argument(
        "--authors", required=True, nargs="+", help="List of authors"
    )
    add_parser.add_argument(
        "--keywords", required=True, nargs="+", help="List of keywords"
    )
    add_parser.add_argument("--bibtex", required=True, help="BibTeX entry")
    add_parser.add_argument("--file", required=True, help="Path to the PDF file")

    # Search papers
    search_parser = subparsers.add_parser("search", help="Search for papers")
    search_parser.add_argument("query", help="Search query")

    # List all papers
    subparsers.add_parser("list", help="List all papers")

    # Get paper details
    details_parser = subparsers.add_parser("details", help="Get paper details")
    details_parser.add_argument("paper_id", type=int, help="Paper ID")

    args = parser.parse_args()

    organizer = ResearchPaperOrganizer(args.db, args.pdf_dir)

    if args.command == "add":
        organizer.add_paper(
            args.title, args.year, args.authors, args.keywords, args.bibtex, args.file
        )
        print(f"Paper '{args.title}' added successfully.")

    elif args.command == "search":
        results = organizer.search_papers(args.query)
        if results:
            for i, (title, year, file_path) in enumerate(results, 1):
                print(f"{i}. {title} ({year}) - {file_path}")
        else:
            print("No results found.")

    elif args.command == "list":
        papers = organizer.list_all_papers()
        for paper_id, title, year in papers:
            print(f"{paper_id}. {title} ({year})")

    elif args.command == "details":
        details = organizer.get_paper_details(args.paper_id)
        if details:
            title, year, file_path, authors, keywords, bibtex = details
            print(f"Title: {title}")
            print(f"Year: {year}")
            print(f"File: {file_path}")
            print(f"Authors: {authors}")
            print(f"Keywords: {keywords}")
            print(f"BibTeX:\n{bibtex}")
        else:
            print(f"No paper found with ID {args.paper_id}")

    organizer.close()


if __name__ == "__main__":
    main()
