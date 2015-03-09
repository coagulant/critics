# coding: utf-8

__version__ = '0.1.0'


def main():
    from .commands import cli
    return cli(auto_envvar_prefix='CRITICS')


if __name__ == '__main__':
    main()
