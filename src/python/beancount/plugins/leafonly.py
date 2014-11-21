"""A plugin that issues errors when more than one commodity is used in an account.
"""
__author__ = "Martin Blais <blais@furius.ca>"

import collections

from beancount.core import getters
from beancount.core import realization

__plugins__ = ('validate_leaf_only',)


LeafOnlyError = collections.namedtuple('LeafOnlyError', 'source message entry')


def validate_leaf_only(entries, unused_options_map):
    """Check for non-leaf accounts that have postings on them.

    This is an extra constraint that you may want to apply optionally. If you
    install this plugin, it will issue errors for all accounts that have
    postings to non-leaf accounts. Some users may want to disallow this and
    enforce that only leaf accounts may have postings on them.

    Args:
      entries: A list of directives.
      unused_options_map: An options map.
    Returns:
      A list of new errors, if any were found.
    """
    real_root = realization.realize(entries, compute_balance=False)

    open_close_map = None # Lazily computed.
    errors = []
    for real_account in realization.iter_children(real_root):
        if len(real_account) > 0 and real_account.postings:

            if open_close_map is None:
                open_close_map = getters.get_account_open_close(entries)

            open_entry = open_close_map[real_account.account][0]
            errors.append(LeafOnlyError(
                open_entry.source,
                "Non-leaf account '{}' has postings on it".format(real_account.account),
                open_entry))

    return entries, errors
