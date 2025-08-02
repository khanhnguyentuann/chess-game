"""
Base Command Pattern Implementation
Provides foundation for all game commands with undo/redo support.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CommandStatus(Enum):
    """Command execution status."""

    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    UNDONE = "undone"


@dataclass
class CommandResult:
    """Result of command execution."""

    success: bool
    message: str = ""
    data: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None


class ICommand(ABC):
    """Base interface for all commands."""

    def __init__(self):
        self.command_id = str(uuid.uuid4())
        self.timestamp = datetime.now()
        self.status = CommandStatus.PENDING
        self.result: Optional[CommandResult] = None

    @abstractmethod
    async def execute(self) -> CommandResult:
        """Execute the command."""
        pass

    @abstractmethod
    async def undo(self) -> CommandResult:
        """Undo the command if possible."""
        pass

    @abstractmethod
    def can_undo(self) -> bool:
        """Check if command can be undone."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of command."""
        pass


class ICommandValidator(ABC):
    """Interface for command validation."""

    @abstractmethod
    def validate(self, command: ICommand) -> bool:
        """Validate command before execution."""
        pass

    @abstractmethod
    def get_validation_errors(self, command: ICommand) -> List[str]:
        """Get detailed validation errors."""
        pass


class CommandExecutor:
    """
    Command executor with undo/redo support and validation.
    """

    def __init__(self, validator: Optional[ICommandValidator] = None):
        self.validator = validator
        self._command_history: List[ICommand] = []
        self._undo_stack: List[ICommand] = []
        self._max_history = 100

    async def execute(self, command: ICommand) -> CommandResult:
        """
        Execute a command with validation and history tracking.

        Args:
            command: Command to execute

        Returns:
            Command execution result
        """
        try:
            # Validate command if validator is present
            if self.validator and not self.validator.validate(command):
                errors = self.validator.get_validation_errors(command)
                return CommandResult(
                    success=False,
                    message=f"Command validation failed: {'; '.join(errors)}",
                )

            # Set status to executing
            command.status = CommandStatus.EXECUTING

            # Execute the command
            result = await command.execute()
            command.result = result

            if result.success:
                command.status = CommandStatus.COMPLETED
                # Add to history
                self._add_to_history(command)
                # Clear undo stack when new command is executed
                self._undo_stack.clear()
            else:
                command.status = CommandStatus.FAILED

            return result

        except Exception as e:
            command.status = CommandStatus.FAILED
            result = CommandResult(
                success=False, message=f"Command execution failed: {str(e)}", error=e
            )
            command.result = result
            return result

    async def undo(self) -> Optional[CommandResult]:
        """
        Undo the last executed command.

        Returns:
            Undo operation result or None if nothing to undo
        """
        if not self._command_history:
            return None

        last_command = self._command_history[-1]

        if not last_command.can_undo():
            return CommandResult(success=False, message="Last command cannot be undone")

        try:
            result = await last_command.undo()

            if result.success:
                last_command.status = CommandStatus.UNDONE
                # Move to undo stack
                self._undo_stack.append(self._command_history.pop())

            return result

        except Exception as e:
            return CommandResult(
                success=False, message=f"Undo failed: {str(e)}", error=e
            )

    async def redo(self) -> Optional[CommandResult]:
        """
        Redo the last undone command.

        Returns:
            Redo operation result or None if nothing to redo
        """
        if not self._undo_stack:
            return None

        command_to_redo = self._undo_stack.pop()

        try:
            # Re-execute the command
            result = await command_to_redo.execute()

            if result.success:
                command_to_redo.status = CommandStatus.COMPLETED
                self._command_history.append(command_to_redo)
            else:
                # Put back in undo stack if redo fails
                self._undo_stack.append(command_to_redo)

            return result

        except Exception as e:
            # Put back in undo stack if redo fails
            self._undo_stack.append(command_to_redo)
            return CommandResult(
                success=False, message=f"Redo failed: {str(e)}", error=e
            )

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return bool(self._command_history and self._command_history[-1].can_undo())

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return bool(self._undo_stack)

    def get_command_history(self) -> List[ICommand]:
        """Get command execution history."""
        return self._command_history.copy()

    def get_undo_stack(self) -> List[ICommand]:
        """Get commands available for redo."""
        return self._undo_stack.copy()

    def clear_history(self) -> None:
        """Clear command history and undo stack."""
        self._command_history.clear()
        self._undo_stack.clear()

    def _add_to_history(self, command: ICommand) -> None:
        """Add command to history with size limit."""
        self._command_history.append(command)

        # Maintain history size limit
        if len(self._command_history) > self._max_history:
            self._command_history = self._command_history[1:]


class CompositeCommand(ICommand):
    """
    Command that executes multiple sub-commands.
    Useful for complex operations that involve multiple steps.
    """

    def __init__(
        self, commands: List[ICommand], description: str = "Composite Command"
    ):
        super().__init__()
        self.commands = commands
        self.description = description
        self._executed_commands: List[ICommand] = []

    async def execute(self) -> CommandResult:
        """Execute all sub-commands in order."""
        self._executed_commands.clear()

        for command in self.commands:
            result = await command.execute()

            if result.success:
                self._executed_commands.append(command)
            else:
                # If any command fails, undo all previously executed commands
                await self._undo_executed_commands()
                return CommandResult(
                    success=False,
                    message=f"Composite command failed at step {len(self._executed_commands) + 1}: {result.message}",
                )

        return CommandResult(
            success=True,
            message=f"Composite command completed successfully ({len(self.commands)} steps)",
            data={"executed_commands": len(self.commands)},
        )

    async def undo(self) -> CommandResult:
        """Undo all executed sub-commands in reverse order."""
        return await self._undo_executed_commands()

    async def _undo_executed_commands(self) -> CommandResult:
        """Helper to undo executed commands."""
        failed_undos = []

        # Undo in reverse order
        for command in reversed(self._executed_commands):
            if command.can_undo():
                result = await command.undo()
                if not result.success:
                    failed_undos.append(command.command_id)

        self._executed_commands.clear()

        if failed_undos:
            return CommandResult(
                success=False, message=f"Some commands failed to undo: {failed_undos}"
            )

        return CommandResult(
            success=True, message="Composite command undone successfully"
        )

    def can_undo(self) -> bool:
        """Check if all executed commands can be undone."""
        return all(cmd.can_undo() for cmd in self._executed_commands)

    def get_description(self) -> str:
        """Get description of composite command."""
        return self.description
