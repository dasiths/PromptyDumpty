"""CLI entry point for dumpty."""

import click
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm, Prompt

from dumpty import __version__
from dumpty.agent_detector import Agent, AgentDetector
from dumpty.downloader import PackageDownloader
from dumpty.installer import FileInstaller
from dumpty.lockfile import LockfileManager
from dumpty.models import PackageManifest, InstalledPackage, InstalledFile, Artifact
from dumpty.utils import (
    calculate_checksum,
    parse_git_tags,
    compare_versions,
    get_project_root,
)

console = Console()

ASCII_ART = r"""
██████╗ ██╗   ██╗███╗   ███╗██████╗ ████████╗██╗   ██╗         ██████╗██╗     ██╗
██╔══██╗██║   ██║████╗ ████║██╔══██╗╚══██╔══╝╚██╗ ██╔╝        ██╔════╝██║     ██║
██║  ██║██║   ██║██╔████╔██║██████╔╝   ██║    ╚████╔╝         ██║     ██║     ██║
██║  ██║██║   ██║██║╚██╔╝██║██╔═══╝    ██║     ╚██╔╝          ██║     ██║     ██║
██████╔╝╚██████╔╝██║ ╚═╝ ██║██║        ██║      ██║           ╚██████╗███████╗██║
╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝      ╚═╝            ╚═════╝╚══════╝╚═╝
"""


def select_categories(
    manifest: PackageManifest,
    all_categories_flag: bool = False,
    categories_flag: Optional[str] = None,
    previous_selection: Optional[List[str]] = None,
    is_update: bool = False,
) -> Optional[List[str]]:
    """Select categories for installation.

    Args:
        manifest: Package manifest with optional categories
        all_categories_flag: If True, select all (skip prompts)
        categories_flag: Comma-separated category names (e.g., "dev,test")
        previous_selection: Previously installed categories (for updates)
        is_update: Whether this is an update operation

    Returns:
        None for "all categories"
        List of category names for specific selection

    Raises:
        ValueError: If categories_flag contains invalid category names
        SystemExit: If user cancels (Ctrl+C)
    """
    # No categories in manifest - return None (install all)
    if manifest.categories is None:
        return None

    # Handle CLI flags
    if all_categories_flag:
        return None  # Install all

    if categories_flag:
        # Parse and validate
        selected = [c.strip() for c in categories_flag.split(",")]
        defined = {cat.name for cat in manifest.categories}

        invalid = set(selected) - defined
        if invalid:
            raise ValueError(
                f"Invalid categories: {', '.join(invalid)}\n"
                f"Available: {', '.join(sorted(defined))}"
            )

        return selected

    # Non-interactive (no TTY) - default to all with warning
    if not sys.stdin.isatty():
        console.print("[yellow]Warning:[/] Non-interactive mode, installing all categories")
        return None

    # Interactive mode
    console.print(f"\n[bold]Package:[/] {manifest.name} v{manifest.version}")
    console.print(f"{manifest.description}\n")
    console.print("This package has categorized artifacts:")

    for cat in manifest.categories:
        console.print(f"  - [cyan]{cat.name}[/]: {cat.description}")
    console.print()

    try:
        # Step 1: Ask if user wants all
        install_all = Confirm.ask("Install all categories?", default=True)

        if install_all:
            return None

        # Step 2: For updates, offer previous selection
        if is_update and previous_selection:
            console.print(f"\nPreviously installed: [cyan]{', '.join(previous_selection)}[/]")
            use_previous = Confirm.ask("Use previous selection?", default=True)

            if use_previous:
                # Validate previous selection still valid
                defined = {cat.name for cat in manifest.categories}
                still_valid = [cat for cat in previous_selection if cat in defined]

                if len(still_valid) < len(previous_selection):
                    removed = set(previous_selection) - set(still_valid)
                    console.print(
                        f"[yellow]Warning:[/] Categories removed from package: {', '.join(removed)}"
                    )

                if still_valid:
                    return still_valid
                else:
                    console.print("[yellow]All previous categories removed, showing picker[/]\n")

        # Step 3: Show category picker
        console.print("\nSelect categories to install:")
        choices = []
        for i, cat in enumerate(manifest.categories, 1):
            console.print(f"  {i}. [cyan]{cat.name}[/] - {cat.description}")
            choices.append(cat.name)
        console.print()

        # Get user input - use plain input() to avoid any Click interaction
        try:
            selection = input('Enter numbers (comma or space separated, e.g., "1 2" or "1,2"): ')
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Installation cancelled[/]")
            sys.exit(0)

        # Parse selection - support both comma and space separated
        try:
            # Replace commas with spaces, then split by whitespace
            normalized = selection.replace(',', ' ')
            indices = [int(x.strip()) for x in normalized.split() if x.strip()]
        except ValueError:
            console.print("[red]Error:[/] Invalid input. Please enter numbers only.")
            sys.exit(1)

        # Validate indices
        invalid_indices = [i for i in indices if i < 1 or i > len(choices)]
        if invalid_indices:
            console.print(f"[red]Error:[/] Invalid selection: {invalid_indices}")
            console.print(f"Valid range: 1-{len(choices)}")
            sys.exit(1)

        # Convert to category names (deduplicate)
        # IMPORTANT: We avoid dict.fromkeys() here due to a bizarre bug where it
        # triggers Click's argument parser, causing category names to be interpreted
        # as command-line arguments (e.g., "Got unexpected extra arguments (documentation planning)")
        # Using manual deduplication instead.
        temp_list = [choices[i - 1] for i in indices]
        selected = []
        for item in temp_list:
            if item not in selected:
                selected.append(item)

        return selected

    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Installation cancelled[/]")
        sys.exit(0)


def filter_artifacts(
    artifacts: List[Artifact], selected_categories: Optional[List[str]]
) -> List[Artifact]:
    """Filter artifacts based on category selection.

    Args:
        artifacts: List of artifacts to filter
        selected_categories: None for all, or list of category names

    Returns:
        Filtered list of artifacts (preserves order)
    """
    if selected_categories is None:
        # Install all
        return artifacts

    return [artifact for artifact in artifacts if artifact.matches_categories(selected_categories)]


@click.group(
    invoke_without_command=True,
    epilog=f"\n[blue]→[/blue] Visit [link=https://dumpty.dev]https://dumpty.dev[/link] for documentation and guides",
)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx):
    """Dumpty - Universal package manager for AI coding assistants."""
    # If no command is provided, show the logo
    if ctx.invoked_subcommand is None:
        console.print(f"[cyan]{ASCII_ART}[/cyan]")
        console.print(
            f"\n[bold cyan]Dumpty[/bold cyan] [dim]v{__version__}[/dim] - Universal package manager for AI coding assistants"
        )
        console.print(f"[blue]→[/blue] [link=https://dumpty.dev]https://dumpty.dev[/link]\n")
        console.print("Run [cyan]dumpty --help[/cyan] to see available commands\n")


@cli.command()
@click.argument("package_url")
@click.option(
    "--agent",
    help="Install for specific agent (copilot, claude, etc.). Defaults to auto-detect.",
)
@click.option("--version", "pkg_version", help="Semantic version tag (e.g., 1.0.0 or v1.0.0)")
@click.option("--commit", "pkg_commit", help="Specific commit hash to install")
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Project root directory. Defaults to git repository root or current directory.",
)
@click.option(
    "--all-categories",
    is_flag=True,
    help="Install all categories without prompting (for categorized packages)",
)
@click.option(
    "--categories",
    help="Comma-separated category names to install (e.g., 'development,testing')",
)
def install(
    package_url: str,
    agent: str,
    pkg_version: str,
    pkg_commit: str,
    project_root: Path,
    all_categories: bool,
    categories: str,
):
    """Install a package from a Git repository."""
    try:
        # Validate mutually exclusive category flags
        if all_categories and categories:
            console.print("[red]Error:[/] Cannot use both --all-categories and --categories")
            console.print("Use one or the other:")
            console.print("  --all-categories        : Install all categories")
            console.print("  --categories dev,test   : Install specific categories")
            sys.exit(1)

        # Determine project root
        project_root = get_project_root(project_root)

        # Validate mutually exclusive options
        if pkg_version and pkg_commit:
            console.print("[red]Error:[/] Cannot use both --version and --commit")
            console.print(
                "Use either --version for tagged releases or --commit for specific commits"
            )
            sys.exit(1)
        # Detect agents
        detector = AgentDetector(project_root)
        detected_agents = detector.detect_agents()

        # Determine target agents
        if agent:
            target_agent = Agent.from_name(agent)
            if not target_agent:
                console.print(
                    f"[red]Error:[/] Unknown agent '{agent}'. "
                    f"Valid options: {', '.join(Agent.all_names())}"
                )
                sys.exit(1)
            target_agents = [target_agent]
        elif detected_agents:
            target_agents = detected_agents
        else:
            console.print(
                "[yellow]Warning:[/] No supported AI coding assistants detected in this project."
            )
            console.print(
                "Please specify an agent with --agent flag or create an agent directory "
                "(e.g., .github, .claude, .cursor)"
            )
            sys.exit(1)

        # Download package
        console.print(f"[blue]Downloading package from {package_url}...[/]")
        downloader = PackageDownloader()
        # Use commit if specified, otherwise use version (or None for latest)
        ref = pkg_commit if pkg_commit else pkg_version
        # Skip version validation for commits
        validate_version = not bool(pkg_commit)
        result = downloader.download(package_url, ref, validate_version=validate_version)

        # Load manifest
        manifest_path = result.manifest_dir / "dumpty.package.yaml"
        if not manifest_path.exists():
            console.print("[red]Error:[/] No dumpty.package.yaml found in package")
            sys.exit(1)

        manifest = PackageManifest.from_file(manifest_path)

        # Determine source directory (external repo takes precedence)
        if result.external_dir:
            source_dir = result.external_dir
            console.print(f"  [dim]Using external repository for source files[/]")
        else:
            source_dir = result.manifest_dir

        # Validate types for each agent before installation
        console.print("[blue]Validating manifest types...[/]")
        from dumpty.agents.registry import get_agent_by_name

        validation_errors = []

        for agent_name, types_dict in manifest.agents.items():
            agent_class = get_agent_by_name(agent_name)
            if agent_class is None:
                console.print(f"  [yellow]⚠[/] Unknown agent '{agent_name}' (skipping validation)")
                continue

            supported_types = agent_class.SUPPORTED_TYPES
            for type_name in types_dict.keys():
                if type_name not in supported_types:
                    validation_errors.append(
                        f"Agent '{agent_name}' does not support type '{type_name}'. "
                        f"Supported: {', '.join(supported_types)}"
                    )

        if validation_errors:
            console.print("[red]Error:[/] Manifest validation failed:")
            for error in validation_errors:
                console.print(f"  - {error}")
            console.print("\nRun [cyan]dumpty validate-manifest[/] for detailed validation")
            sys.exit(1)
        console.print("  [green]✓[/] All types are valid")

        # Validate files exist (check in source directory)
        missing_files = manifest.validate_files_exist(source_dir)
        if missing_files:
            console.print("[red]Error:[/] Package manifest references missing files:")
            for missing in missing_files:
                console.print(f"  - {missing}")
            sys.exit(1)

        # Category selection (only if manifest has categories)
        selected_categories = select_categories(
            manifest=manifest,
            all_categories_flag=all_categories,
            categories_flag=categories,
            previous_selection=None,
            is_update=False,
        )

        # Display selected categories
        if manifest.categories and selected_categories is not None:
            console.print(
                f"\n[blue]Installing {manifest.name} v{manifest.version} for categories:[/] "
                f"[cyan]{', '.join(selected_categories)}[/]"
            )
        elif manifest.categories:
            console.print(
                f"\n[blue]Installing {manifest.name} v{manifest.version} (all categories)[/]"
            )

        # Install files for each agent
        installer = FileInstaller(project_root)
        lockfile = LockfileManager(project_root)

        # Check if package is already installed
        existing_package = lockfile.get_package(manifest.name)
        if existing_package:
            console.print(
                f"\n[yellow]⚠️  Warning:[/] Package '{manifest.name}' is already installed"
            )
            console.print(
                f"  [dim]Current:[/] v{existing_package.version} from [cyan]{existing_package.source}[/]"
            )
            console.print(f"  [dim]New:[/]     v{manifest.version} from [cyan]{package_url}[/]")

            # Check if sources are different
            if existing_package.source != package_url:
                console.print(
                    f"\n[red]⚠️  Different source detected![/] The package name is the same but from a different repository."
                )

            # Ask for confirmation
            console.print()
            try:
                from rich.prompt import Confirm

                if not Confirm.ask(
                    "Do you want to replace the existing installation?", default=False
                ):
                    console.print("[yellow]Installation cancelled[/]")
                    sys.exit(0)
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Installation cancelled[/]")
                sys.exit(0)

            console.print()

        installed_files = {}
        total_installed = 0

        console.print(f"\n[green]Installing {manifest.name} v{manifest.version}[/]")

        for target_agent in target_agents:
            agent_name = target_agent.name.lower()

            # Check if package supports this agent
            if agent_name not in manifest.agents:
                console.print(
                    f"[yellow]Warning:[/] Package does not support {target_agent.display_name}, skipping"
                )
                continue

            # Ensure agent directory exists
            detector.ensure_agent_directory(target_agent)

            # Get types and artifacts for this agent
            types = manifest.agents[agent_name]

            # Apply category filtering to all artifacts
            filtered_types = {}
            total_artifacts = 0
            for type_name, artifacts in types.items():
                filtered = filter_artifacts(artifacts, selected_categories)
                if filtered:  # Only include types with remaining artifacts
                    filtered_types[type_name] = filtered
                    total_artifacts += len(filtered)

            if total_artifacts == 0:
                console.print(
                    f"[yellow]Warning:[/] No artifacts match selected categories for {target_agent.display_name}, skipping"
                )
                continue

            console.print(f"\n[cyan]{target_agent.display_name}[/] ({total_artifacts} artifacts):")

            # Prepare source files list for install_package (now with types)
            source_files = []
            for type_name, artifacts in filtered_types.items():
                for artifact in artifacts:
                    source_files.append(
                        (source_dir / artifact.file, artifact.installed_path, type_name)
                    )

            # Call install_package which will trigger pre/post install hooks
            results = installer.install_package(
                source_dir, source_files, target_agent, manifest.name
            )

            # Process results for lockfile
            agent_files = []
            artifact_idx = 0
            for type_name, artifacts in filtered_types.items():
                for artifact in artifacts:
                    dest_path, checksum = results[artifact_idx]
                    artifact_idx += 1

                    # Make path relative to project root for lockfile
                    try:
                        rel_path = dest_path.relative_to(project_root)
                    except ValueError:
                        rel_path = dest_path

                    agent_files.append(
                        InstalledFile(
                            source=artifact.file,
                            installed=str(rel_path),
                            checksum=checksum,
                        )
                    )

                    console.print(f"  [green]✓[/] {artifact.file} → {rel_path}")
                    total_installed += 1

            installed_files[agent_name] = agent_files

        if total_installed == 0:
            console.print(
                "[yellow]Warning:[/] No files were installed (package may not support detected agents)"
            )
            sys.exit(1)

        # Update lockfile
        commit_hash = downloader.get_resolved_commit(result.manifest_dir)
        manifest_checksum = calculate_checksum(manifest_path)

        # Track external repo info if present
        external_repo = None
        if result.external_dir:
            from dumpty.models import ExternalRepoInfo

            external_repo = ExternalRepoInfo(
                source=manifest.get_external_repo_url(), commit=result.external_commit
            )

        installed_package = InstalledPackage(
            name=manifest.name,
            version=manifest.version,
            source=package_url,
            source_type="git",
            resolved=commit_hash,
            installed_at=datetime.utcnow().isoformat() + "Z",
            installed_for=[a.name.lower() for a in target_agents],
            files=installed_files,
            manifest_checksum=manifest_checksum,
            installed_categories=selected_categories,
            description=manifest.description,
            author=manifest.author,
            homepage=manifest.homepage,
            license=manifest.license,
            external_repo=external_repo,
        )

        lockfile.add_package(installed_package)

        console.print(f"\n[green]✓ Installation complete![/] {total_installed} files installed.")

        # Clean up cache after successful installation
        downloader.cleanup_cache(result.manifest_dir)
        if result.external_dir:
            downloader.cleanup_cache(result.external_dir)

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Project root directory. Defaults to git repository root or current directory.",
)
def list(verbose: bool, project_root: Path):
    """List installed packages."""
    try:
        # Determine project root
        project_root = get_project_root(project_root, warn=False)

        lockfile = LockfileManager(project_root)
        packages = lockfile.list_packages()

        if not packages:
            console.print("[yellow]No packages installed.[/]")
            return

        console.print(f"\n[bold]Installed packages:[/] ({len(packages)})\n")

        if verbose:
            # Detailed view
            for pkg in packages:
                console.print(f"[cyan]{pkg.name}[/] v{pkg.version}")
                console.print(f"  Source: {pkg.source}")
                console.print(f"  Installed: {pkg.installed_at}")
                console.print(f"  Agents: {', '.join(pkg.installed_for)}")
                console.print("  Files:")
                for agent, files in pkg.files.items():
                    console.print(f"    {agent}: {len(files)} files")
                    for f in files:
                        console.print(f"      - {f.installed}")
                console.print()
        else:
            # Table view
            table = Table()
            table.add_column("Package", style="cyan")
            table.add_column("Version", style="green")
            table.add_column("Agents", style="yellow")
            table.add_column("Files", justify="right")

            for pkg in packages:
                total_files = sum(len(files) for files in pkg.files.values())
                table.add_row(
                    pkg.name,
                    pkg.version,
                    ", ".join(pkg.installed_for),
                    str(total_files),
                )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--agent",
    help="Initialize for specific agent. Defaults to auto-detect.",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Project root directory. Defaults to git repository root or current directory.",
)
def init(agent: str, project_root: Path):
    """Initialize dumpty in the current project."""
    try:
        # Determine project root
        project_root = get_project_root(project_root)

        # Detect or validate agents
        detector = AgentDetector(project_root)
        detected_agents = detector.detect_agents()

        if agent:
            target_agent = Agent.from_name(agent)
            if not target_agent:
                console.print(
                    f"[red]Error:[/] Unknown agent '{agent}'. "
                    f"Valid options: {', '.join(Agent.all_names())}"
                )
                sys.exit(1)

            # Ensure directory exists
            detector.ensure_agent_directory(target_agent)
            console.print(
                f"[green]✓[/] Created {target_agent.directory}/ directory for {target_agent.display_name}"
            )
        elif detected_agents:
            console.print("[green]Detected agents:[/]")
            for a in detected_agents:
                console.print(f"  - {a.display_name} ({a.directory}/)")
        else:
            console.print(
                "[yellow]No supported AI coding assistants detected.[/] You can create agent directories manually:"
            )
            console.print("\nSupported agents:")
            for a in Agent:
                console.print(f"  - {a.display_name}: {a.directory}/")
            console.print("\nOr use: [cyan]dumpty init --agent <agent-name>[/] to create one")
            return

        # Create lockfile if it doesn't exist
        lockfile_path = project_root / "dumpty.lock"
        if not lockfile_path.exists():
            lockfile = LockfileManager(project_root)
            lockfile._save()
            console.print("[green]✓[/] Created dumpty.lock")
        else:
            console.print("[yellow]dumpty.lock already exists[/]")

        console.print("\n[green]✓ Initialization complete![/]")
        console.print("\nYou can now install packages with: [cyan]dumpty install <package-url>[/]")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.argument("package_name")
@click.option(
    "--agent",
    help="Uninstall from specific agent only (copilot, claude, etc.). Otherwise uninstall from all agents.",
)
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Project root directory. Defaults to git repository root or current directory.",
)
def uninstall(package_name: str, agent: str, project_root: Path):
    """Uninstall a package."""
    try:
        # Determine project root
        project_root = get_project_root(project_root, warn=False)

        # Load lockfile
        lockfile = LockfileManager(project_root)

        # Check if package exists
        package = lockfile.get_package(package_name)
        if not package:
            console.print(f"[red]Error:[/] Package '{package_name}' is not installed")
            sys.exit(1)

        # Determine target agents
        if agent:
            # Validate agent name
            target_agent = Agent.from_name(agent)
            if not target_agent:
                console.print(
                    f"[red]Error:[/] Unknown agent '{agent}'. "
                    f"Valid options: {', '.join(Agent.all_names())}"
                )
                sys.exit(1)

            agent_name = target_agent.name.lower()

            # Check if package is installed for this agent
            if agent_name not in package.installed_for:
                console.print(
                    f"[yellow]Warning:[/] Package '{package_name}' is not installed for {target_agent.display_name}"
                )
                sys.exit(0)

            target_agents = [target_agent]
        else:
            # Uninstall from all agents
            target_agents = [Agent.from_name(a) for a in package.installed_for]

        # Uninstall files for each agent
        installer = FileInstaller(project_root)
        total_removed = 0

        console.print(f"\n[blue]Uninstalling {package_name} v{package.version}[/]")

        for target_agent in target_agents:
            agent_name = target_agent.name.lower()

            # Count files for this agent
            files_count = len(package.files.get(agent_name, []))

            # Uninstall package directory for this agent
            installer.uninstall_package(target_agent, package_name)

            console.print(
                f"  [green]✓[/] Removed from {target_agent.display_name} ({files_count} files)"
            )
            total_removed += files_count

        # Update lockfile
        if agent:
            # Partial uninstall - update installed_for list
            remaining_agents = [a for a in package.installed_for if a != agent_name]

            if remaining_agents:
                # Update package with remaining agents
                package.installed_for = remaining_agents

                # Remove files for uninstalled agent
                if agent_name in package.files:
                    del package.files[agent_name]

                lockfile.add_package(package)
                console.print(
                    f"\n[yellow]Package still installed for: {', '.join(remaining_agents)}[/]"
                )
            else:
                # No agents left, remove completely
                lockfile.remove_package(package_name)
        else:
            # Full uninstall - remove from lockfile
            lockfile.remove_package(package_name)

        console.print(f"\n[green]✓ Uninstallation complete![/] {total_removed} files removed.")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.argument("package_name", required=False)
@click.option("--all", "update_all", is_flag=True, help="Update all installed packages")
@click.option("--version", "target_version", help="Semantic version tag (e.g., 2.0.0 or v2.0.0)")
@click.option("--commit", "target_commit", help="Specific commit hash to update to")
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Project root directory. Defaults to git repository root or current directory.",
)
@click.option(
    "--all-categories",
    is_flag=True,
    help="Install all categories without prompting (for categorized packages)",
)
@click.option(
    "--categories",
    help="Comma-separated category names to install (e.g., 'development,testing')",
)
def update(
    package_name: str,
    update_all: bool,
    target_version: str,
    target_commit: str,
    project_root: Path,
    all_categories: bool,
    categories: str,
):
    """Update installed packages to newer versions."""
    try:
        # Validate mutually exclusive category flags
        if all_categories and categories:
            console.print("[red]Error:[/] Cannot use both --all-categories and --categories")
            console.print("Use one or the other:")
            console.print("  --all-categories        : Install all categories")
            console.print("  --categories dev,test   : Install specific categories")
            sys.exit(1)

        # Determine project root
        project_root = get_project_root(project_root, warn=False)

        # Validate options
        if target_version and target_commit:
            console.print("[red]Error:[/] Cannot use both --version and --commit")
            console.print(
                "Use either --version for tagged releases or --commit for specific commits"
            )
            sys.exit(1)
        if update_all and (target_version or target_commit):
            console.print("[red]Error:[/] Cannot use --version or --commit with --all flag")
            console.print("Specify a package name when updating to a specific version or commit")
            sys.exit(1)

        if target_version and not package_name:
            console.print("[red]Error:[/] --version requires a package name")
            console.print("Use: dumpty update <package-name> --version 1.0.0")
            sys.exit(1)

        if target_commit and not package_name:
            console.print("[red]Error:[/] --commit requires a package name")
            console.print("Use: dumpty update <package-name> --commit <hash>")
            sys.exit(1)

        # Load lockfile
        lockfile = LockfileManager(project_root)
        packages = lockfile.list_packages()

        if not packages:
            console.print("[yellow]No packages installed.[/]")
            return

        # Determine which packages to update
        if update_all:
            packages_to_update = packages
        elif package_name:
            pkg = lockfile.get_package(package_name)
            if not pkg:
                console.print(f"[red]Error:[/] Package '{package_name}' is not installed")
                sys.exit(1)
            packages_to_update = [pkg]
        else:
            console.print("[red]Error:[/] Please specify a package name or use --all flag")
            sys.exit(1)

        # Initialize downloader
        downloader = PackageDownloader()
        installer = FileInstaller(project_root)
        detector = AgentDetector(project_root)

        updated_count = 0

        for package in packages_to_update:
            console.print(f"\n[blue]Checking {package.name} v{package.version}...[/]")

            try:
                # Handle commit-based update (skip version checking)
                if target_commit:
                    console.print(f"  [cyan]Updating to commit:[/] {target_commit[:8]}...")

                    # Download at specific commit
                    result = downloader.download(
                        package.source, target_commit, validate_version=False
                    )

                    # Load manifest (without version validation)
                    manifest_path = result.manifest_dir / "dumpty.package.yaml"
                    if not manifest_path.exists():
                        console.print("  [red]Error:[/] No dumpty.package.yaml found in package")
                        continue

                    manifest = PackageManifest.from_file(manifest_path)

                    # Determine source directory (external repo takes precedence)
                    if result.external_dir:
                        source_dir = result.external_dir
                    else:
                        source_dir = result.manifest_dir

                    # Continue with installation logic (skip to uninstall/install section)
                    target_version_str = manifest.version
                    target_tag = target_commit
                else:
                    # Version-based update (existing logic)
                    # Fetch available tags
                    tags = downloader.git_ops.fetch_tags(package.source)

                    if not tags:
                        console.print("  [yellow]No version tags found in repository[/]")
                        continue

                    # Parse versions
                    versions = parse_git_tags(tags)

                    if not versions:
                        console.print("  [yellow]No valid semantic versions found[/]")
                        continue

                # Determine target version
                if target_version and not target_commit:
                    # Use specified version
                    target_tag = None
                    target_ver = None

                    # Find the matching version
                    for tag_name, ver in versions:
                        if tag_name == target_version or tag_name == f"v{target_version}":
                            target_tag = tag_name
                            target_ver = ver
                            break

                    if not target_tag:
                        console.print(f"  [red]Version {target_version} not found[/]")
                        continue

                    # Set target_version_str for later use
                    target_version_str = str(target_ver)
                elif not target_commit:
                    # Use latest version (only if not using commit)
                    target_tag, target_ver = versions[0]
                    target_version_str = str(target_ver)

                # Version comparison and messaging (skip for commits)
                if not target_commit:
                    # Compare versions
                    current_version = package.version

                    # Skip if same version (unless explicit version specified)
                    if current_version == target_version_str and not target_version:
                        console.print(f"  [green]Already up to date[/] (v{current_version})")
                        continue

                    # Check if it's an upgrade, downgrade, or reinstall
                    if target_version:
                        # Explicit version requested - allow any change
                        if current_version == target_version_str:
                            console.print(f"  [cyan]Reinstalling:[/] v{target_version_str}")
                        elif compare_versions(current_version, target_version_str):
                            console.print(
                                f"  [cyan]Updating:[/] v{current_version} → v{target_version_str}"
                            )
                        else:
                            console.print(
                                f"  [yellow]Downgrading:[/] v{current_version} → v{target_version_str}"
                            )
                    else:
                        # Auto-update to latest - only upgrade
                        if not compare_versions(current_version, target_version_str):
                            console.print(f"  [green]Already up to date[/] (v{current_version})")
                            continue
                        console.print(
                            f"  [cyan]Update available:[/] v{current_version} → v{target_version_str}"
                        )

                    # Download new version
                    console.print(f"  [blue]Downloading v{target_version_str}...[/]")
                    result = downloader.download(package.source, target_tag)

                # For commits, result was already downloaded above

                # Load manifest (only if not already loaded for commit)
                if not target_commit:
                    manifest_path = result.manifest_dir / "dumpty.package.yaml"
                    if not manifest_path.exists():
                        console.print("  [red]Error:[/] No dumpty.package.yaml found in package")
                        continue

                    manifest = PackageManifest.from_file(manifest_path)

                    # Determine source directory (external repo takes precedence)
                    if result.external_dir:
                        source_dir = result.external_dir
                    else:
                        source_dir = result.manifest_dir

                # Validate types for each agent before update
                from dumpty.agents.registry import get_agent_by_name

                validation_errors = []

                for agent_name, types_dict in manifest.agents.items():
                    agent_class = get_agent_by_name(agent_name)
                    if agent_class is None:
                        continue

                    supported_types = agent_class.SUPPORTED_TYPES
                    for type_name in types_dict.keys():
                        if type_name not in supported_types:
                            validation_errors.append(
                                f"Agent '{agent_name}' does not support type '{type_name}'. "
                                f"Supported: {', '.join(supported_types)}"
                            )

                if validation_errors:
                    console.print("  [red]Error:[/] Manifest validation failed:")
                    for error in validation_errors:
                        console.print(f"    - {error}")
                    console.print(
                        "\n  Run [cyan]dumpty validate-manifest[/] for detailed validation"
                    )
                    continue

                # Validate files exist (check in source directory)
                missing_files = manifest.validate_files_exist(source_dir)
                if missing_files:
                    console.print("  [red]Error:[/] Package manifest references missing files:")
                    for missing in missing_files:
                        console.print(f"    - {missing}")
                    continue

                # Category selection (offer previous selection for updates)
                selected_categories = select_categories(
                    manifest=manifest,
                    all_categories_flag=all_categories,
                    categories_flag=categories,
                    previous_selection=package.installed_categories,
                    is_update=True,
                )

                # Display selected categories
                if manifest.categories and selected_categories is not None:
                    console.print(
                        f"  [blue]Using categories:[/] [cyan]{', '.join(selected_categories)}[/]"
                    )
                elif manifest.categories:
                    console.print(f"  [blue]Using all categories[/]")

                # Uninstall old version
                console.print("  [blue]Removing old version...[/]")
                for agent_name in package.installed_for:
                    agent = Agent.from_name(agent_name)
                    if agent:
                        installer.uninstall_package(agent, package.name)

                # Install new version
                console.print(f"  [blue]Installing v{target_version_str}...[/]")

                installed_files = {}
                total_installed = 0

                for agent_name in package.installed_for:
                    agent = Agent.from_name(agent_name)
                    if not agent:
                        continue

                    # Check if package supports this agent
                    if agent_name not in manifest.agents:
                        console.print(
                            f"    [yellow]Warning:[/] New version doesn't support {agent.display_name}, skipping"
                        )
                        continue

                    # Ensure agent directory exists
                    detector.ensure_agent_directory(agent)

                    # Get types and artifacts for this agent (nested structure)
                    types = manifest.agents[agent_name]

                    # Apply category filtering to all artifacts
                    filtered_types = {}
                    for type_name, artifacts in types.items():
                        filtered = filter_artifacts(artifacts, selected_categories)
                        if filtered:  # Only include types with remaining artifacts
                            filtered_types[type_name] = filtered

                    if not filtered_types:
                        console.print(
                            f"    [yellow]Warning:[/] No artifacts match selected categories for {agent.display_name}, skipping"
                        )
                        continue

                    # Prepare source files list for install_package (now with types)
                    source_files = []
                    for type_name, artifacts in filtered_types.items():
                        for artifact in artifacts:
                            source_files.append(
                                (source_dir / artifact.file, artifact.installed_path, type_name)
                            )

                    # Call install_package which will trigger pre/post install hooks
                    results = installer.install_package(
                        source_dir, source_files, agent, manifest.name
                    )

                    # Process results for lockfile
                    agent_files = []
                    artifact_idx = 0
                    for type_name, artifacts in filtered_types.items():
                        for artifact in artifacts:
                            dest_path, checksum = results[artifact_idx]
                            artifact_idx += 1

                            # Make path relative to project root for lockfile
                            try:
                                rel_path = dest_path.relative_to(project_root)
                            except ValueError:
                                rel_path = dest_path

                            agent_files.append(
                                InstalledFile(
                                    source=artifact.file,
                                    installed=str(rel_path),
                                    checksum=checksum,
                                )
                            )
                            total_installed += 1

                    installed_files[agent_name] = agent_files

                # Update lockfile
                commit_hash = downloader.get_resolved_commit(result.manifest_dir)
                manifest_checksum = calculate_checksum(manifest_path)

                # Track external repo info if present
                external_repo = None
                if result.external_dir:
                    from dumpty.models import ExternalRepoInfo

                    external_repo = ExternalRepoInfo(
                        source=manifest.get_external_repo_url(), commit=result.external_commit
                    )

                updated_package = InstalledPackage(
                    name=manifest.name,
                    version=manifest.version,
                    source=package.source,
                    source_type="git",
                    resolved=commit_hash,
                    installed_at=datetime.utcnow().isoformat() + "Z",
                    installed_for=package.installed_for,
                    files=installed_files,
                    manifest_checksum=manifest_checksum,
                    installed_categories=selected_categories,
                    description=manifest.description,
                    author=manifest.author,
                    homepage=manifest.homepage,
                    license=manifest.license,
                    external_repo=external_repo,
                )

                lockfile.add_package(updated_package)

                console.print(
                    f"  [green]✓ Updated to v{target_version_str}[/] ({total_installed} files)"
                )
                updated_count += 1

                # Clean up cache after successful update
                downloader.cleanup_cache(result.manifest_dir)
                if result.external_dir:
                    downloader.cleanup_cache(result.external_dir)

            except Exception as e:
                console.print(f"  [red]Error updating {package.name}:[/] {e}")
                continue

        if updated_count > 0:
            console.print(f"\n[green]✓ Update complete![/] {updated_count} package(s) updated.")
        else:
            console.print("\n[yellow]No packages were updated.[/]")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.argument("package_name")
@click.option(
    "--project-root",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    help="Project root directory. Defaults to git repository root or current directory.",
)
def show(package_name: str, project_root: Path):
    """Display detailed information about an installed package."""
    try:
        # Determine project root
        project_root = get_project_root(project_root, warn=False)

        # Load lockfile
        lockfile = LockfileManager(project_root)

        # Find package in lockfile
        package = lockfile.get_package(package_name)
        if not package:
            console.print(f"[red]Error:[/] Package '{package_name}' is not installed")
            console.print("\nRun [cyan]dumpty list[/] to see installed packages")
            sys.exit(1)

        # Display package information
        _display_package_info(package)

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


def _display_package_info(package: InstalledPackage):
    """Display formatted package information using Rich."""

    # Header section
    console.print(f"\n[bold cyan]{package.name}[/] [dim]v{package.version}[/]")
    console.print()

    # Metadata section
    console.print("[bold]Package Information[/]")
    console.print(f"  Description: {package.description or '[dim]N/A[/]'}")
    console.print(f"  Author:      {package.author or '[dim]N/A[/]'}")
    console.print(f"  License:     {package.license or '[dim]N/A[/]'}")
    console.print(f"  Homepage:    {package.homepage or '[dim]N/A[/]'}")
    console.print()

    # Installation details
    console.print("[bold]Installation Details[/]")
    console.print(f"  Source:      {package.source}")
    console.print(f"  Version:     {package.resolved}")
    console.print(f"  Installed:   {package.installed_at}")

    # Display external repo info if present
    if package.external_repo:
        console.print()
        console.print("[bold]External Repository[/]")
        console.print(f"  Source:      {package.external_repo.source}")
        console.print(f"  Commit:      {package.external_repo.commit}")
        console.print(f"  [dim]Note: Package files are sourced from external repository[/]")

    console.print()

    # Installed files grouped by agent
    console.print("[bold]Installed Files[/]")

    # Group files by agent
    files_by_agent = {}
    for agent_name in package.installed_for:
        if agent_name in package.files:
            files_by_agent[agent_name] = package.files[agent_name]

    # Display each agent's files
    for agent_name, files in sorted(files_by_agent.items()):
        console.print(f"\n  [cyan]{agent_name.upper()}[/] ({len(files)} files)")

        # Create table for files
        table = Table(
            show_header=True,
            header_style="bold",
            box=None,
            padding=(0, 2),
        )
        table.add_column("Artifact", style="dim")
        table.add_column("Path")

        for file in sorted(files, key=lambda f: f.installed):
            # Extract artifact name from source file (if available)
            artifact_name = Path(file.source).stem if file.source else "-"
            table.add_row(artifact_name, file.installed)

        console.print(table)


@cli.command()
@click.argument(
    "manifest_path", type=click.Path(exists=True, dir_okay=False, path_type=Path), required=False
)
def validate_manifest(manifest_path: Path):
    """Validate a package manifest file.

    Checks if the manifest can be parsed and validates that specified types
    are supported by each agent.

    MANIFEST_PATH: Path to dumpty.package.yaml (defaults to current directory)
    """
    try:
        # Default to dumpty.package.yaml in current directory
        if manifest_path is None:
            manifest_path = Path.cwd() / "dumpty.package.yaml"
            if not manifest_path.exists():
                console.print("[red]Error:[/] No dumpty.package.yaml found in current directory")
                console.print("\nUsage: [cyan]dumpty validate-manifest [MANIFEST_PATH][/]")
                sys.exit(1)

        console.print(f"\n[bold]Validating manifest:[/] {manifest_path}")
        console.print()

        # Try to load and parse the manifest
        try:
            manifest = PackageManifest.from_file(manifest_path)
        except ValueError as e:
            console.print(f"[red]✗ Validation failed:[/] {e}")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]✗ Parse error:[/] {e}")
            sys.exit(1)

        # Basic validation passed
        console.print(f"[green]✓[/] Manifest parsed successfully")
        console.print(f"  Package: [cyan]{manifest.name}[/] v{manifest.version}")
        console.print(f"  Manifest version: {manifest.manifest_version}")
        console.print()

        # Validate types for each agent
        console.print("[bold]Agent Type Validation:[/]")
        console.print()

        validation_passed = True
        for agent_name, types_dict in manifest.agents.items():
            # Get agent to check supported types
            from dumpty.agents.registry import get_agent_by_name

            agent_class = get_agent_by_name(agent_name)

            if agent_class is None:
                console.print(
                    f"  [yellow]⚠[/] [cyan]{agent_name}[/]: Unknown agent (skipping validation)"
                )
                continue

            supported_types = agent_class.SUPPORTED_TYPES
            console.print(f"  [cyan]{agent_name}[/]:")
            console.print(f"    Supported types: {', '.join(supported_types)}")

            # Check each type used in manifest
            for type_name in types_dict.keys():
                if type_name in supported_types:
                    artifact_count = len(types_dict[type_name])
                    console.print(
                        f"    [green]✓[/] {type_name} ({artifact_count} artifact{'s' if artifact_count != 1 else ''})"
                    )
                else:
                    validation_passed = False
                    console.print(f"    [red]✗[/] {type_name} - NOT SUPPORTED by this agent")
            console.print()

        # Final summary
        if validation_passed:
            console.print("[bold green]✓ Manifest is valid![/]")
            console.print()
        else:
            console.print(
                "[bold red]✗ Validation failed:[/] Some types are not supported by their agents"
            )
            console.print()
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)

    console.print()


if __name__ == "__main__":
    cli()
