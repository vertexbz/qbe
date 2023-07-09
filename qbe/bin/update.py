from __future__ import annotations
import os
import time
from itertools import chain
import qbe.cli as cli
from qbe.handler import NotificationBag
from qbe.handler import handler
from qbe.package_provider import UpdateResult, dependency_provider, build_dependency
from qbe.package_provider.internal import InternalDependency
from qbe.package import load as package_load, load_config as package_load_config, Result, Status, Section, Detail
from qbe.feature_provider import AVAILABLE_PROVIDERS
from qbe.config import Config
from qbe.trigger import multihandler


@cli.command(short_help='Update dependencies')
@cli.pass_config
def update(config: Config):
    os.makedirs(config.paths.packages, exist_ok=True)
    error = False

    notifications = NotificationBag()
    messages: dict[str, list[str]] = {}
    for dependency in config.requires:
        line = cli.Line(prefix=f'Processing package {cli.bold(os.path.basename(dependency.name))}: ')
        result = Result()

        line.print(cli.dim('updating package...'))
        time.sleep(0.25)

        updatable_dependency = dependency
        if isinstance(dependency, InternalDependency):
            package_config = package_load_config(dependency.qbe_definition)

            if isinstance(package_config, dict) and 'data-source' in package_config:
                package_config['data-source'].update({'local': package_config['name']})
                updatable_dependency = build_dependency(package_config['data-source'], config.paths)
                dependency.local = updatable_dependency.local

        provider_cls = dependency_provider(updatable_dependency)
        if provider_cls is None:
            continue

        update_result = provider_cls(updatable_dependency).update()
        if update_result is UpdateResult.INSTALLED:
            result.section('package').installed('installed package')
        elif update_result is UpdateResult.UPDATED:
            result.section('package').updated('updated package')
        else:
            result.section('package').unchanged('package up to date')

        package = package_load(dependency)
        pkg_name = os.path.basename(package.name)
        line.prefix = f'Processing package {cli.bold(pkg_name)}: '

        pkg_messages: list[str] = []
        messages[pkg_name] = pkg_messages

        line.print(cli.dim('processing providers...'))
        time.sleep(0.25)

        for provider_name, provider_cls in AVAILABLE_PROVIDERS.items():
            if provider_name in package.provides:
                provider = provider_cls(config, package, dependency)
                provider.process(package.provides[provider_name], line, result.section(provider_name))

        line.print(_color_result(result.status))
        line.finish()

        trigger_handler = multihandler(
            config=config,
            package=package,
            dependency=dependency,
            section=result.section('triggers'),
            messages=pkg_messages
        )
        status = result.status
        if status == Status.INSTALLED and len(package.triggers.installed) > 0:
            for trigger in package.triggers.installed:
                trigger_handler(trigger)
        if status == Status.UPDATED and len(package.triggers.updated) > 0:
            for trigger in package.triggers.updated:
                trigger_handler(trigger)
        if len(package.triggers.always) > 0:
            for trigger in package.triggers.always:
                trigger_handler(trigger)

        for section in result.sections:
            if len(section.details) == 0:
                continue

            print(_color_section(section) + ':')
            for detail in section.details:
                print('  ' + _color_detail(detail))

        if result.status == Status.ERROR:
            error = True

        notifications.merge(result.notifications)

    if len(notifications.items) > 0:
        print('handler:')
        for notification in notifications.items:
            print('  ' + str(notification) + ': ', end='')
            try:
                handler(notification).handle(notification)
                print(cli.updated('ok'))
            except Exception as e:
                cli.error_with_trace(e)

    if len(list(chain.from_iterable(messages.values()))):
        print()
        for pkg, msgs in messages.items():
            for msg in msgs:
                print(cli.message('message from '), end='')
                print(cli.message_important(pkg), end='')
                print(cli.message(':'))
                print(msg)

        print(cli.message('---------------'))
        print()

    return 1 if error else 0


def _color_result(status: Status):
    if status == Status.UNCHANGED:
        return cli.success('ok')
    if status == Status.INSTALLED:
        return cli.updated('installed')
    if status == Status.UPDATED:
        return cli.updated('updated')
    if status == Status.ERROR:
        return cli.error('error')


def _color_section(section: Section):
    if section.status == Status.UNCHANGED:
        return cli.dim(section.name)
    if section.status == Status.UPDATED or section.status == Status.INSTALLED:
        return cli.success(section.name)
    if section.status == Status.ERROR:
        return cli.error(section.name)


def _color_detail(detail: Detail):
    if detail.status == Status.UNCHANGED:
        return cli.dim(detail.text)
    if detail.status == Status.UPDATED or detail.status == Status.INSTALLED:
        pre, sep, end = detail.text.partition(':')
        if sep == '':
            return cli.success(detail.text)
        return cli.dim(pre + sep) + cli.success(end)
    if detail.status == Status.ERROR:
        pre, sep, end = detail.text.partition(':')
        if sep == '':
            return cli.error(detail.text)
        return cli.dim(pre + sep) + cli.error(end)
