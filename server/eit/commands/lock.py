# -*- coding: utf-8 -*-
"""

    @author: Fabio Erculiani <lxnay@sabayon.org>
    @contact: lxnay@sabayon.org
    @copyright: Fabio Erculiani
    @license: GPL-2

    B{Entropy Infrastructure Toolkit}.

"""
import sys
import argparse

from entropy.i18n import _
from entropy.output import darkgreen, brown, teal, purple, blue, darkred
from entropy.transceivers import EntropyTransceiver

from eit.commands.descriptor import EitCommandDescriptor
from eit.commands.command import EitCommand


class EitLock(EitCommand):
    """
    Main Eit lock command.
    """

    NAME = "lock"
    ALIASES = []
    ALLOW_UNPRIVILEGED = True

    def __init__(self, args):
        EitCommand.__init__(self, args)
        self._repository_id = None
        self._action_lock = True
        self._client = False
        self._quiet = False
        self._name = EitLock.NAME

    def parse(self):
        descriptor = EitCommandDescriptor.obtain_descriptor(
            EitLock.NAME)
        parser = argparse.ArgumentParser(
            description=descriptor.get_description(),
            formatter_class=argparse.RawDescriptionHelpFormatter,
            prog="%s %s" % (sys.argv[0], self._name))

        parser.add_argument("repo", nargs=1, metavar="<repo>",
                            help=_("repository"))

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--client", action="store_true", default=False,
            help=_('affect entropy clients only'))
        group.add_argument(
            "--status", action="store_true", default=False,
            help=_('show current status'))

        parser.add_argument("--quiet", "-q", action="store_true",
           default=self._quiet,
           help=_('quiet output, for scripting purposes'))

        try:
            nsargs = parser.parse_args(self._args)
        except IOError:
            return parser.print_help, []

        self._client = nsargs.client
        self._repository_id = nsargs.repo[0]
        self._quiet = nsargs.quiet
        if nsargs.status:
            return self._call_unlocked, [self._status, None]
        if self._client:
            return self._call_locked, [self._client_lock,
                                       self._repository_id]
        else:
            return self._call_locked, [self._lock, self._repository_id]

    def _status(self, entropy_server):
        """
        Actual Eit lock|unlock --status code. Just show repo status.
        """
        if not self._quiet:
            entropy_server.output(
                "%s:" % (darkgreen(_("Mirrors status")),),
                header=brown(" * "))

        dbstatus = entropy_server.Mirrors.mirrors_status(
            self._repository_id)
        for uri, server_lock, client_lock in dbstatus:

            host = EntropyTransceiver.get_uri_name(uri)
            if not self._quiet:
                entropy_server.output(
                    "[%s]" % (purple(host),),
                    header=darkgreen(" @@ "))

            if server_lock:
                lock_str = darkred(_("Locked"))
                quiet_lock_str = "locked"
            else:
                lock_str = darkgreen(_("Unlocked"))
                quiet_lock_str = "unlocked"
            if self._quiet:
                entropy_server.output(
                    "%s server %s" % (host, quiet_lock_str),
                    level="generic")
            else:
                entropy_server.output(
                    "%s: %s" % (blue(_("server")), lock_str),
                    header=brown("  # "))

            if client_lock:
                lock_str = darkred(_("Locked"))
                quiet_lock_str = "locked"
            else:
                lock_str = darkgreen(_("Unlocked"))
                quiet_lock_str = "unlocked"
            if self._quiet:
                entropy_server.output(
                    "%s client %s" % (host, quiet_lock_str),
                    level="generic")
            else:
                entropy_server.output(
                    "%s: %s" % (blue(_("client")), lock_str),
                    header=brown("  # "))

        return 0

    def _lock(self, entropy_server):
        """
        Actual Eit lock code. self._action_lock is determining if it's
        lock or unlock.
        """
        done = entropy_server.Mirrors.lock_mirrors(
            self._repository_id, self._action_lock,
            quiet = self._quiet)
        if not done:
            return 1
        return 0

    def _client_lock(self, entropy_server):
        """
        Actual Eit lock code (for --client only).
        """
        done = entropy_server.Mirrors.lock_mirrors_for_download(
            self._repository_id, self._action_lock,
            quiet = self._quiet)
        if not done:
            return 1
        return 0

EitCommandDescriptor.register(
    EitCommandDescriptor(
        EitLock,
        EitLock.NAME,
        _('lock repository'))
    )


class EitUnlock(EitLock):
    """
    Main Eit unlock command.
    """

    NAME = "unlock"
    ALIASES = []
    ALLOW_UNPRIVILEGED = True

    def __init__(self, args):
        EitLock.__init__(self, args)
        self._repository_id = None
        self._action_lock = False
        self._name = EitUnlock.NAME

EitCommandDescriptor.register(
    EitCommandDescriptor(
        EitUnlock,
        EitUnlock.NAME,
        _('unlock repository'))
    )