import click

from napalm.storage import WorkflowStorage


@click.group(help="Manage workflows (create/ delete/ list)")
@click.pass_context
def workflows(ctx):
    pass


@workflows.command(help="Create a new workflow")
@click.argument("workflow-name")
@click.pass_context
def create(ctx, workflow_name):
    storage = WorkflowStorage(ctx.obj["storage"])

    if storage.get_workflow(workflow_name) or storage.get_workflow(workflow_name) == []:
        click.echo(f"workflow {workflow_name} already exists")
        exit(1)

    storage.create_workflow(workflow_name)
    click.echo(f"Successfully created workflow {workflow_name}")


@workflows.command(help="Delete a workflow")
@click.argument("workflow-name")
@click.pass_context
def delete(ctx, workflow_name):
    storage = WorkflowStorage(ctx.obj["storage"])

    if storage.get_workflow(workflow_name) in (None, []):
        click.echo(f"workflow {workflow_name} does not exist")
        exit(1)

    storage.remove_workflow(workflow_name)
    click.echo(f"Successfully deleted workflow {workflow_name}")


@workflows.command(help="List all workflows")
@click.pass_context
def list(ctx):
    storage = WorkflowStorage(ctx.obj["storage"])

    click.echo("workflows:")
    for workflow in storage.list:
        click.echo(f"  - {workflow}")


# Managing existing workflows
@click.group(help="Manage a specific workflow")
@click.argument("workflow-name")
@click.pass_context
def workflow(ctx, workflow_name):
    ctx.ensure_object(dict)
    ctx.obj["workflow_name"] = workflow_name
    storage = WorkflowStorage(ctx.obj["storage"])

    if storage.get_workflow(workflow_name) is None:
        click.echo(f"workflow {workflow_name} does not exist")
        exit(1)


@workflow.command(help="Add collection from workflow")
@click.argument("collection")
@click.pass_context
def add(ctx, collection):
    workflow_name = ctx.obj["workflow_name"]
    storage_provider = ctx.obj["storage"]

    storage = WorkflowStorage(storage_provider)

    # TODO: ensure that target is a valid & installed collection
    storage.add_to_workflow(workflow_name, collection)
    click.echo(
        f"Successfully added collection {collection} to workflow {workflow_name}"
    )


@workflow.command(help="Remove collection from workflow")
@click.argument("collection")
@click.pass_context
def remove(ctx, collection):
    workflow_name = ctx.obj["workflow_name"]
    storage_provider = ctx.obj["storage"]

    storage = WorkflowStorage(storage_provider)
    workflow_workflows = storage.get_workflow(workflow_name)

    if collection not in workflow_workflows:
        click.echo(f"Collection {collection} not in workflow {workflow_name}")
        return

    storage.remove_from_workflow(workflow_name, collection)

    click.echo(
        f"Successfully removed collection {collection} from workflow {workflow_name}"
    )


@workflow.command(help="List workflows in workflow", name="list")
@click.pass_context
def _list(ctx):
    workflow_name = ctx.obj["workflow_name"]
    storage_provider = ctx.obj["storage"]

    storage = WorkflowStorage(storage_provider)
    workflow_workflows = storage.get_workflow(workflow_name)

    click.echo(f"workflow {workflow_name} contains:")
    for collection in workflow_workflows:
        click.echo(f"  - {collection}")
