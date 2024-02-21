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
    if workflow_name == "all":
        click.echo("Cannot create a workflow with keyword 'all'")
        exit(1)

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


@workflow.command(help="List filters in workflow", name="list-filters")
@click.pass_context
def list_filters(ctx):
    workflow_name = ctx.obj["workflow_name"]
    storage_provider = ctx.obj["storage"]

    storage = WorkflowStorage(storage_provider)
    filters = storage.filters.get(workflow_name, {})

    if not filters:
        click.echo(f"workflow {workflow_name} does not contain any filters")
        return

    if not any(f for f, values in filters.values()):
        click.echo(f"workflow {workflow_name} does not contain any filters")
        return

    click.echo(f"workflow {workflow_name} filters:")
    for filter_name, filter_value in filters.items():
        if not filter_value:
            continue

        click.echo(f"  - {filter_name}: ")
        (allow_deny, values) = filter_value
        for value in values:
            click.echo(f"    - {allow_deny} {value}")


def _filter(ctx, filter_name, filter_value, allow_deny):
    workflow_name = ctx.obj["workflow_name"]
    storage_provider = ctx.obj["storage"]

    storage = WorkflowStorage(storage_provider)

    current_filter = storage.get_filter(workflow_name, filter_name)
    _allow_deny, values = current_filter if current_filter is not None else (None, [])

    if _allow_deny and _allow_deny != allow_deny:
        click.echo(
            f"Filter {filter_name} already exists as a {allow_deny} filter and cannot be updated."
        )
        exit(1)

    values.append(filter_value)

    storage.set_filter(workflow_name, filter_name, (allow_deny, values))

    click.echo(
        f"Successfully added {allow_deny} list filter {filter_name} = {filter_value} to workflow {workflow_name}"
    )


@workflow.command(help="Add allowlist filter to workflow", name="include")
@click.argument("filter-name")
@click.argument("filter-value")
@click.pass_context
def include(ctx, filter_name, filter_value):
    _filter(ctx, filter_name, filter_value, "allow")


@workflow.command(help="Add denylist filter to workflow", name="exclude")
@click.argument("filter-name")
@click.argument("filter-value")
@click.pass_context
def exclude(ctx, filter_name, filter_value):
    _filter(ctx, filter_name, filter_value, "deny")


@workflow.command(help="Reset workflow filter")
@click.argument("filter-name")
@click.pass_context
def reset_filter(ctx, filter_name):
    workflow_name = ctx.obj["workflow_name"]
    storage_provider = ctx.obj["storage"]

    storage = WorkflowStorage(storage_provider)

    storage.set_filter(workflow_name, filter_name, None)

    click.echo(f"Successfully reset filter {filter_name} in workflow {workflow_name}")
