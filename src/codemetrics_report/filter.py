import numpy as np


IGNORE_PATHS = ('.', 'docs', 'doc', 'tests', 'test', 'notebooks')
IGNORE_LANGS = ('reStructuredText', 'Markdown', 'make')
IGNORE_EXTS = ('geo', 'xmf', 'xdmf', 'h5', 'hdf5', 'xml', 'json',
               'yml', 'yaml', 'csv', 'svg', 'png')


def exclude_paths(df, ignore_paths=IGNORE_PATHS, col_name='path'):
    if '.' in ignore_paths:
        df = exclude_root_files(df, col_name=col_name)
        ignore_paths = list(ignore_paths)
        ignore_paths.remove('.')

    exc_indices = _exclude_str(df[col_name], ignore_paths, method='startswith')
    return df[~exc_indices]


def exclude_root_files(df, col_name='path'):
    inc_indices = _exclude_str(df[col_name], ['/'], 'contains')
    return df[inc_indices]


def exclude_languages(df, ignore_langs=IGNORE_LANGS):
    exc_indices = _exclude_str(df['language'], ignore_langs, method='match')

    return df[~exc_indices]


def exclude_file_types(df, ignore_exts=IGNORE_EXTS, col_name='path'):
    ignore_exts = [f'.{ext}' for ext in ignore_exts]
    exc_indices = _exclude_str(df[col_name], ignore_exts, 'endswith')

    return df[~exc_indices]


def include_only_paths(df, include_paths, col_name='path'):
    for path in include_paths:
        inc_indices = _exclude_str(df[col_name], include_paths,
                                   method='startswith')

    return df[inc_indices]


def _exclude_str(df_col, ignores, method):
    exc_indices = np.array([False] * df_col.size)

    for ignore in ignores:
        fnc = getattr(df_col.str, method)
        exc_indices = np.logical_or(exc_indices, fnc(ignore))

    return exc_indices
