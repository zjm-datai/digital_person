
import logging
import click

logger = logging.getLogger(__name__)

@click.command("upgrade-db", help="Upgrade the database")
def upgrade_db():
    """
    虽然 flask_migrate 已经提供了 upgrade 命令，但是为了避免多个进程同时执行数据库迁移，这里添加了迁移锁。
    同时我们可以添加更多控制和日志操作。
    """

    click.echo("Preparing database migration...")

    # TODO 
    # 添加迁移锁

    try:

        click.echo(click.style("Starting database migration.", fg="green"))

        # run db migration
        import flask_migrate
        flask_migrate.upgrade()

        click.echo(click.style("Database migration successful!", fg="green"))

    except Exception:
        logger.exception("Failed to execute database migration")