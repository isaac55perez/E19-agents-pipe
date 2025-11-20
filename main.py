#!/usr/bin/env python3
"""
Main application menu for E19 Agents Pipeline.

This script provides a CLI interface to manage and execute the 4-agent pipeline:
- Agent1: Gmail Exercise Extractor
- Agent2: Repository Python Analyzer
- Agent3: Excel Greeting Transformer
- Agent4: Gmail Draft Creator

The application allows users to:
1. Clear the output folder
2. Run individual agents (1-4)
3. Run the complete pipeline sequentially
4. Exit the application
"""

import os
import sys
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentPipeline:
    """Manages execution of the E19 agents pipeline."""

    # Agent information mapping
    AGENTS = {
        1: {
            'name': 'Gmail Exercise Extractor',
            'path': '.claude/agents/agent1',
            'description': 'Extracts exercise submissions from Gmail'
        },
        2: {
            'name': 'Repository Python Analyzer',
            'path': '.claude/agents/agent2',
            'description': 'Analyzes code quality of repositories'
        },
        3: {
            'name': 'Excel Greeting Transformer',
            'path': '.claude/agents/agent3',
            'description': 'Adds personalized greetings based on grades'
        },
        4: {
            'name': 'Gmail Draft Creator',
            'path': '.claude/agents/agent4',
            'description': 'Creates Gmail drafts with feedback'
        }
    }

    OUTPUT_DIR = 'output'

    def __init__(self):
        """Initialize the pipeline manager."""
        self.project_root = Path(__file__).parent
        self.output_path = self.project_root / self.OUTPUT_DIR

    def clear_screen(self) -> None:
        """Clear the terminal screen (cross-platform)."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "=" * 50)
        print("E19 Agents Pipeline - Main Menu")
        print("=" * 50)
        print("1. Clear output folder")
        print("2. Run Agent1 (Gmail Exercise Extractor)")
        print("3. Run Agent2 (Repository Python Analyzer)")
        print("4. Run Agent3 (Excel Greeting Transformer)")
        print("5. Run Agent4 (Gmail Draft Creator)")
        print("6. Run full pipeline (Agent1 → Agent2 → Agent3 → Agent4)")
        print("7. Exit")
        print("=" * 50)

    def get_user_choice(self) -> str:
        """
        Get and validate user input.

        Returns:
            str: User's choice (1-7)
        """
        while True:
            try:
                choice = input("\nEnter your choice (1-7): ").strip()
                if choice in ['1', '2', '3', '4', '5', '6', '7']:
                    return choice
                print("Invalid choice. Please enter a number between 1 and 7.")
            except EOFError:
                # Handle EOF gracefully (end of input stream)
                print("\nEnd of input reached. Exiting...")
                sys.exit(0)

    def clear_output_folder(self) -> None:
        """
        Clear all files in the output folder.

        Displays count of deleted files on success.
        """
        print("\nClearing output folder...")
        try:
            if self.output_path.exists():
                files_deleted = 0
                for item in self.output_path.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                            files_deleted += 1
                        elif item.is_dir():
                            shutil.rmtree(item)
                            files_deleted += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete {item}: {e}")

                print(f"✓ Output folder cleared ({files_deleted} items deleted)")
                logger.info(f"Deleted {files_deleted} items from output folder")
            else:
                print("Output folder does not exist. Creating it...")
                self.output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"✗ Error clearing output folder: {e}")
            logger.error(f"Failed to clear output folder: {e}")

    def run_agent(self, agent_number: int) -> bool:
        """
        Execute a specific agent.

        Args:
            agent_number: Agent number (1-4)

        Returns:
            bool: True if agent executed successfully, False otherwise
        """
        if agent_number not in self.AGENTS:
            print(f"Invalid agent number: {agent_number}")
            return False

        agent_info = self.AGENTS[agent_number]
        agent_path = self.project_root / agent_info['path']

        # Verify agent directory exists
        if not agent_path.exists():
            print(f"✗ Agent{agent_number} directory not found: {agent_path}")
            logger.error(f"Agent{agent_number} directory not found at {agent_path}")
            return False

        print(f"\n{'=' * 50}")
        print(f"Running Agent{agent_number}: {agent_info['name']}")
        print(f"Description: {agent_info['description']}")
        print(f"{'=' * 50}\n")

        try:
            # Run agent's main.py
            result = subprocess.run(
                [sys.executable, 'main.py'],
                cwd=str(agent_path),
                capture_output=False,
                timeout=600  # 10-minute timeout per agent
            )

            if result.returncode == 0:
                print(f"\n✓ Agent{agent_number} completed successfully")
                logger.info(f"Agent{agent_number} executed successfully")
                return True
            else:
                print(f"\n✗ Agent{agent_number} failed with exit code {result.returncode}")
                logger.error(f"Agent{agent_number} failed with exit code {result.returncode}")
                return False

        except subprocess.TimeoutExpired:
            print(f"\n✗ Agent{agent_number} timed out (exceeded 10 minutes)")
            logger.error(f"Agent{agent_number} execution timed out")
            return False
        except Exception as e:
            print(f"\n✗ Error running Agent{agent_number}: {e}")
            logger.error(f"Error running Agent{agent_number}: {e}")
            return False

    def run_pipeline(self) -> bool:
        """
        Execute the complete pipeline (all 4 agents in sequence).

        Returns:
            bool: True if all agents executed successfully, False if any failed
        """
        print(f"\n{'=' * 50}")
        print("Running Full Pipeline (Agent1 → Agent2 → Agent3 → Agent4)")
        print(f"{'=' * 50}\n")

        all_success = True
        results = {}

        for agent_num in [1, 2, 3, 4]:
            print(f"\n[Stage {agent_num}/4] Running Agent{agent_num}...")
            success = self.run_agent(agent_num)
            results[agent_num] = success

            if not success:
                print(f"\n⚠ Pipeline stopped at Agent{agent_num} due to failure")
                all_success = False
                break

        # Display pipeline summary
        print(f"\n{'=' * 50}")
        print("Pipeline Execution Summary")
        print(f"{'=' * 50}")
        for agent_num in [1, 2, 3, 4]:
            status = "✓ Success" if results.get(agent_num, False) else "✗ Failed/Skipped"
            agent_name = self.AGENTS[agent_num]['name']
            print(f"Agent{agent_num}: {status}")
            print(f"  {agent_name}")

        print(f"{'=' * 50}")
        if all_success:
            print("✓ Full pipeline completed successfully!")
        else:
            print("✗ Pipeline execution failed or was interrupted")

        return all_success

    def run(self) -> None:
        """Main application loop."""
        try:
            while True:
                self.display_menu()
                choice = self.get_user_choice()

                if choice == '1':
                    self.clear_output_folder()
                elif choice == '2':
                    self.run_agent(1)
                elif choice == '3':
                    self.run_agent(2)
                elif choice == '4':
                    self.run_agent(3)
                elif choice == '5':
                    self.run_agent(4)
                elif choice == '6':
                    self.run_pipeline()
                elif choice == '7':
                    print("\nExiting E19 Agents Pipeline. Goodbye!")
                    break

                input("\nPress Enter to return to menu...")

        except KeyboardInterrupt:
            print("\n\nApplication interrupted by user. Exiting...")
            logger.info("Application interrupted by user")
            sys.exit(0)
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            logger.error(f"Unexpected error in main loop: {e}")
            sys.exit(1)


def main():
    """Entry point for the application."""
    pipeline = AgentPipeline()
    pipeline.run()


if __name__ == '__main__':
    main()
