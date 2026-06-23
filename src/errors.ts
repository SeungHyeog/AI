export class CommandExecutionError extends Error {
  readonly command: string

  constructor(command: string, message: string) {
    super(message)
    this.name = "CommandExecutionError"
    this.command = command
  }
}
