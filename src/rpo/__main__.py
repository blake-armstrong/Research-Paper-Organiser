import argparse
from .rpo import ResearchPaperOrganiser
from .config import get_config, update_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Research Paper Organizer")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Config command
    config_parser = subparsers.add_parser("config", help="Update configuration")

    # Add paper
    add_parser = subparsers.add_parser("add", help="Add a new paper")
    add_parser.add_argument("--bibtex", required=True, help="BibTeX entry")
    add_parser.add_argument("--file", required=True, help="Path to the PDF file")
    add_parser.add_argument(
        "--keywords", required=True, nargs="+", help="List of keywords"
    )

    # Remove paper
    remove_parser = subparsers.add_parser("remove", help="Remove a paper")
    remove_parser.add_argument("paper_id", type=int, help="Paper ID to remove")

    # Search papers
    search_parser = subparsers.add_parser("search", help="Search for papers")
    search_parser.add_argument("query", help="Search query")

    # List all papers
    subparsers.add_parser("list", help="List all papers")

    # Get paper details
    details_parser = subparsers.add_parser("details", help="Get paper details")
    details_parser.add_argument("paper_id", type=int, help="Paper ID")

    # Open paper
    open_parser = subparsers.add_parser("open", help="Open the PDF file for a paper")
    open_parser.add_argument("paper_id", type=int, help="Paper ID to open")

    args = parser.parse_args()

    if args.command == "config":
        update_config()
        return

    config = get_config()
    if config is None:
        print("Configuration is required before using the program.")
        return

    organizer = ResearchPaperOrganiser(config["db_path"], config["pdf_dir"])

    if args.command == "add":
        try:
            organizer.add_paper(args.bibtex, args.file, args.keywords)
            print("Paper added successfully.")
        except ValueError as e:
            print(f"Error: {e}")

    elif args.command == "remove":
        try:
            organizer.remove_paper(args.paper_id)
            print(f"Paper with ID {args.paper_id} removed successfully.")
        except ValueError as e:
            print(f"Error: {e}")

    elif args.command == "list":
        papers = organizer.list_all_papers()
        for paper_id, authors, year, journal, title, file_path in papers:
            print(f"{paper_id}. {authors} ({year}). {journal}. {title}")

    elif args.command == "search":
        results = organizer.search_papers(args.query)
        if results:
            for paper_id, authors, year, journal, title, file_path in results:
                print(f"{paper_id}. {authors} ({year}). {journal}. {title}")
        else:
            print("No results found.")

    elif args.command == "details":
        details = organizer.get_paper_details(args.paper_id)
        if details:
            title, year, file_path, journal, authors, keywords, bibtex = details
            print(f"Title: {title}")
            print(f"Year: {year}")
            print(f"Journal: {journal}")
            print(f"File: {file_path}")
            print(f"Authors: {authors}")
            print(f"Keywords: {keywords}")
            print(f"BibTeX:\n{bibtex}")
        else:
            print(f"No paper found with ID {args.paper_id}")

    elif args.command == "open":
        organizer.open_paper(args.paper_id)

    organizer.close()


if __name__ == "__main__":
    main()
