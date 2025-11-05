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
from dumpty.utils import calculate_checksum, parse_git_tags, compare_versions

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """Dumpty - Universal package manager for AI agent artifacts."""
    pass


@cli.command()
@click.argument("package_url")
@click.option(
    "--agent",
    help="Install for specific agent (copilot, claude, etc.). Defaults to auto-detect.",
)
@click.option("--version", "pkg_version", help="Package version (tag, branch, or commit)")
def install(package_url: str, agent: str, pkg_version: str):
    """Install a package from a Git repository."""
    try:
        # Detect agents
        detector = AgentDetector()
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
            console.print("[yellow]Warning:[/] No AI agents detected in this project.")
            console.print(
                "Please specify an agent with --agent flag or create an agent directory "
                "(e.g., .github, .claude, .cursor)"
            )
            sys.exit(1)

        # Download package
        console.print(f"[blue]Downloading package from {package_url}...[/]")
        downloader = PackageDownloader()
        package_dir = downloader.download(package_url, pkg_version)

        # Load manifest
        manifest_path = package_dir / "dumpty.package.yaml"
        if not manifest_path.exists():
            console.print("[red]Error:[/] No dumpty.package.yaml found in package")
            sys.exit(1)

        manifest = PackageManifest.from_file(manifest_path)

        # Validate files exist
        missing_files = manifest.validate_files_exist(package_dir)
        if missing_files:
            console.print("[red]Error:[/] Package manifest references missing files:")
            for missing in missing_files:
                console.print(f"  - {missing}")
            sys.exit(1)

        # Install files for each agent
        installer = FileInstaller()
        lockfile = LockfileManager()
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

            # Install artifacts
            artifacts = manifest.agents[agent_name]
            console.print(f"\n[cyan]{target_agent.display_name}[/] ({len(artifacts)} artifacts):")

            agent_files = []
            for artifact in artifacts:
                source_file = package_dir / artifact.file
                dest_path, checksum = installer.install_file(
                    source_file, target_agent, manifest.name, artifact.installed_path
                )

                # Make path relative to project root for lockfile
                try:
                    rel_path = dest_path.relative_to(Path.cwd())
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
        )

        lockfile.add_package(installed_package)

        console.print(f"\n[green]✓ Installation complete![/] {total_installed} files installed.")

    except Exception as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information")
def list(verbose: bool):
    """List installed packages."""
    try:
        lockfile = LockfileManager()
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
def init(agent: str):
    """Initialize dumpty in the current project."""
    try:
        # Detect or validate agents
        detector = AgentDetector()
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
                "[yellow]No AI agents detected.[/] You can create agent directories manually:"
            )
            console.print("\nSupported agents:")
            for a in Agent:
                console.print(f"  - {a.display_name}: {a.directory}/")
            console.print("\nOr use: [cyan]dumpty init --agent <agent-name>[/] to create one")
            return

        # Create lockfile if it doesn't exist
        lockfile_path = Path.cwd() / "dumpty.lock"
        if not lockfile_path.exists():
            lockfile = LockfileManager()
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
def uninstall(package_name: str, agent: str):
    """Uninstall a package."""
    try:
        # Load lockfile
        lockfile = LockfileManager()

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
        installer = FileInstaller()
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
@click.option("--version", "target_version", help="Update to specific version")
def update(package_name: str, update_all: bool, target_version: str):
    """Update installed packages to newer versions."""
    try:
        # Load lockfile
        lockfile = LockfileManager()
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
        installer = FileInstaller()
        detector = AgentDetector()

        updated_count = 0

        for package in packages_to_update:
            console.print(f"\n[blue]Checking {package.name} v{package.version}...[/]")

            try:
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
                if target_version:
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
                else:
                    # Use latest version
                    target_tag, target_ver = versions[0]

                # Compare versions
                current_version = package.version
                target_version_str = str(target_ver)

                if not compare_versions(current_version, target_version_str):
                    console.print(f"  [green]Already up to date[/] (v{current_version})")
                    continue

                console.print(
                    f"  [cyan]Update available:[/] v{current_version} → v{target_version_str}"
                )

                # Download new version
                console.print(f"  [blue]Downloading v{target_version_str}...[/]")
                package_dir = downloader.download(package.source, target_tag)

                # Load manifest
                manifest_path = package_dir / "dumpty.package.yaml"
                if not manifest_path.exists():
                    console.print("  [red]Error:[/] No dumpty.package.yaml found in package")
                    continue

                manifest = PackageManifest.from_file(manifest_path)

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

                    # Install artifacts
                    artifacts = manifest.agents[agent_name]
                    agent_files = []

                    for artifact in artifacts:
                        source_file = package_dir / artifact.file
                        dest_path, checksum = installer.install_file(
                            source_file, agent, manifest.name, artifact.installed_path
                        )

                        # Make path relative to project root for lockfile
                        try:
                            rel_path = dest_path.relative_to(Path.cwd())
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
                )

                lockfile.add_package(updated_package)

                console.print(
                    f"  [green]✓ Updated to v{target_version_str}[/] ({total_installed} files)"
                )
                updated_count += 1

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


if __name__ == "__main__":
    cli()
