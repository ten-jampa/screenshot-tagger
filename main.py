import argparse
import os
import sys
from src.storage import init_db, add_screenshot, search, get_stats

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg")


def _is_image_file(filename: str) -> bool:
    """Check if the filename ends with a supported image suffix (case-insensitive)."""
    return filename.lower().endswith(IMAGE_SUFFIXES)


def ingest_directory(directory: str) -> None:
    """
    Process supported image files in the given directory, skipping already processed files.
    """
    for filename in sorted(os.listdir(directory)):
        if _is_image_file(filename):
            add_screenshot(os.path.join(directory, filename))


def resolve_named_directory(name: str) -> str:
    """Handle convenient directory names for user CLI (desktop, documents, downloads)."""
    named_dirs = {
        'desktop': '~/Desktop',
        'documents': '~/Documents',
        'downloads': '~/Downloads'
    }
    if name and name.lower() in named_dirs:
        return os.path.expanduser(named_dirs[name.lower()])
    return name


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Manage and search tagged screenshots in the database."
    )
    parser.add_argument(
        "--dir",
        "--directory",
        dest="directory",
        type=str,
        nargs="?",
        default=None,
        help="Path to directory containing screenshots (optional if using --query)."
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        metavar="TEXT",
        help="Search file name, tag, and description (ingest only occurs with --add)"
    )
    parser.add_argument(
        "--add",
        action="store_true",
        help="With --query, ingest the directory before searching. Ignored without --query."
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about the database."
    )

    args = parser.parse_args()

    # Interpret well-known directory short names, if provided
    args.directory = resolve_named_directory(args.directory) if args.directory else None

    # Querying mode
    if args.query is not None:
        if args.add:
            if args.directory is None:
                print("Error: --add specified but no directory provided to ingest.", file=sys.stderr)
                sys.exit(1)
            directory = os.path.normpath(os.path.expanduser(args.directory))
            if not os.path.isdir(directory):
                print(f"Not a directory: {args.directory}", file=sys.stderr)
                sys.exit(1)
            ingest_directory(directory)
            print(f"Ingested images from {directory}.")
        query = args.query.lower()
        results = search(query)
        print(f"Search results for '{query}':")
        for row in results:
            print(row)
        sys.exit(0)

    # Stats mode implemented
    if args.stats:
        stats = get_stats()
        print("Database statistics:")
        print(f"  Total screenshots: {stats['total_screenshots']}")
        print("  Tags and counts:")
        for tag, count in stats['tag_counts'].items():
            print(f"    {tag}: {count}")
        print(f"  All unique tags: {', '.join(stats['all_tags'])}")
        sys.exit(0)

    # Ingestion mode
    if args.directory is None:
        print(
            "Error: Directory argument required for ingestion (when --query is not used).",
            file=sys.stderr)
        parser.print_usage()
        sys.exit(1)

    directory = os.path.normpath(os.path.expanduser(args.directory))
    if not os.path.isdir(directory):
        print(f"Not a directory: {args.directory}", file=sys.stderr)
        sys.exit(1)

    ingest_directory(directory)
    print(f"Ingested images from {directory}.")


if __name__ == "__main__":
    init_db()
    main()
