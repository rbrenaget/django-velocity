"""
Celery task definitions.

Following HackSoft styleguide: Tasks are thin wrappers that call services.
Tasks should NOT contain business logic - they should delegate to services.

Example usage:
    # Call task asynchronously
    example_task.delay("Hello!")

    # Call task with countdown
    example_task.apply_async(args=["Hello!"], countdown=60)
"""

from celery import shared_task


@shared_task
def example_task(message: str) -> str:
    """
    Example Celery task.

    This is a simple example task. In real applications, tasks should
    call services for business logic, not implement it directly.

    Example with service pattern:
        from .services import process_something
        process_something(data=data)
    """
    return f"Processed: {message}"
