# coding: utf-8

__version__ = '0.2.0'
envvar_prefix = 'CRITICS'


def main():
    from .commands import cli
    return cli(auto_envvar_prefix=envvar_prefix)


if __name__ == '__main__':
    main()
