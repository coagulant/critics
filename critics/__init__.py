# coding: utf-8

__version__ = '1.0.0'
envvar_prefix = 'CRITICS'


def main():
    from .commands import cli
    return cli(auto_envvar_prefix=envvar_prefix)


if __name__ == '__main__':
    main()
