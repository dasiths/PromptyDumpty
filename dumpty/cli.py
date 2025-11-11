"""CLI entry point for dumpty."""

import click
import sys
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table

from dumpty import __version__
from dumpty.agent_detector import Agent, AgentDetector
from dumpty.downloader import PackageDownloader
from dumpty.installer import FileInstaller
from dumpty.lockfile import LockfileManager
from dumpty.models import PackageManifest, InstalledPackage, InstalledFile
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
def install(package_url: str, agent: str, pkg_version: str, pkg_commit: str, project_root: Path):
    """Install a package from a Git repository."""
    try:
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
        package_dir = downloader.download(package_url, ref, validate_version=validate_version)

        # Load manifest
        manifest_path = package_dir / "dumpty.package.yaml"
        if not manifest_path.exists():
            console.print("[red]Error:[/] No dumpty.package.yaml found in package")
            sys.exit(1)

        manifest = PackageManifest.from_file(manifest_path)

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

        # Validate files exist
        missing_files = manifest.validate_files_exist(package_dir)
        if missing_files:
            console.print("[red]Error:[/] Package manifest references missing files:")
            for missing in missing_files:
                console.print(f"  - {missing}")
            sys.exit(1)

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

            # Count total artifacts across all types
            total_artifacts = sum(len(artifacts) for artifacts in types.values())
            console.print(f"\n[cyan]{target_agent.display_name}[/] ({total_artifacts} artifacts):")

            # Prepare source files list for install_package (now with types)
            source_files = []
            for type_name, artifacts in types.items():
                for artifact in artifacts:
                    source_files.append(
                        (package_dir / artifact.file, artifact.installed_path, type_name)
                    )

            # Call install_package which will trigger pre/post install hooks
            results = installer.install_package(source_files, target_agent, manifest.name)

            # Process results for lockfile
            agent_files = []
            artifact_idx = 0
            for type_name, artifacts in types.items():
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
        commit_hash = downloader.get_resolved_commit(package_dir)
        manifest_checksum = calculate_checksum(manifest_path)

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
            description=manifest.description,
            author=manifest.author,
            homepage=manifest.homepage,
            license=manifest.license,
        )

        lockfile.add_package(installed_package)

        console.print(f"\n[green]✓ Installation complete![/] {total_installed} files installed.")

        # Clean up cache after successful installation
        downloader.cleanup_cache(package_dir)

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
def update(
    package_name: str, update_all: bool, target_version: str, target_commit: str, project_root: Path
):
    """Update installed packages to newer versions."""
    try:
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
                    package_dir = downloader.download(
                        package.source, target_commit, validate_version=False
                    )

                    # Load manifest (without version validation)
                    manifest_path = package_dir / "dumpty.package.yaml"
                    if not manifest_path.exists():
                        console.print("  [red]Error:[/] No dumpty.package.yaml found in package")
                        continue

                    manifest = PackageManifest.from_file(manifest_path)

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
                    package_dir = downloader.download(package.source, target_tag)

                # For commits, package_dir was already downloaded above

                # Load manifest (only if not already loaded for commit)
                if not target_commit:
                    manifest_path = package_dir / "dumpty.package.yaml"
                    if not manifest_path.exists():
                        console.print("  [red]Error:[/] No dumpty.package.yaml found in package")
                        continue

                    manifest = PackageManifest.from_file(manifest_path)

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

                # Validate files exist
                missing_files = manifest.validate_files_exist(package_dir)
                if missing_files:
                    console.print("  [red]Error:[/] Package manifest references missing files:")
                    for missing in missing_files:
                        console.print(f"    - {missing}")
                    continue

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

                    # Prepare source files list for install_package (now with types)
                    source_files = []
                    for type_name, artifacts in types.items():
                        for artifact in artifacts:
                            source_files.append(
                                (package_dir / artifact.file, artifact.installed_path, type_name)
                            )

                    # Call install_package which will trigger pre/post install hooks
                    results = installer.install_package(source_files, agent, manifest.name)

                    # Process results for lockfile
                    agent_files = []
                    artifact_idx = 0
                    for type_name, artifacts in types.items():
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
                commit_hash = downloader.get_resolved_commit(package_dir)
                manifest_checksum = calculate_checksum(manifest_path)

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
                    description=manifest.description,
                    author=manifest.author,
                    homepage=manifest.homepage,
                    license=manifest.license,
                )

                lockfile.add_package(updated_package)

                console.print(
                    f"  [green]✓ Updated to v{target_version_str}[/] ({total_installed} files)"
                )
                updated_count += 1

                # Clean up cache after successful update
                downloader.cleanup_cache(package_dir)

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
