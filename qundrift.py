# qundrift.py - refresh applied patches in mq patch queue
#
# Copyright 2009 L. David Baron <dbaron@dbaron.org> (and contributors to
# mq.py, from which a few pieces were taken)
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2, incorporated herein by reference.

'''clean up patch drift in an mq patch queue

This extension will rewrite applied patches in an mq patch queue to
match the diff as they are currently applied.  In other words, it
updates the applied patches so that they will re-apply without fuzz or
line offsets.

It provides a single command: qundrift
'''

from mercurial.i18n import _
from mercurial.node import bin
from mercurial import util, cmdutil
from hgext.mq import patchheader

def qundrift(ui, repo, *args, **opts):
    """rewrite given patches to clean up patch drift"""
    applied = opts.get('applied')
    rev = opts.get('rev')
    if applied:
        if rev:
            raise util.Abort(_("qundrift requires only one of -a or -r"))
        patches = repo.mq.applied
    else:
        if not rev:
            raise util.Abort(_("qundrift requires either -a or -r"))
        patches = []
        for r in cmdutil.revrange(repo, rev):
            patch = None
            for qp in repo.mq.applied:
                # qr.rev is hex and r is an integer
                if bin(qp.rev) == repo.changelog.node(r):
                    patch = qp
                    break;
            if patch is None:
                raise util.Abort(_("revision in range is not applied"))
            patches.append(patch)
    for p in patches:
        print "updating patch " + p.name
        ph = patchheader(repo.mq.join(p.name))
        patchf = repo.mq.opener(p.name, 'w')
        comments = str(ph)
        if comments:
            patchf.write(comments)
        repo.mq.printdiff(repo, repo.mq.qparents(repo, bin(p.rev)), p.rev, fp=patchf)
        patchf.close()

cmdtable = {
    "qundrift":
    (qundrift,
     [('a', 'applied', None, _('rewrite all applied patches')),
      ('r', 'rev', [], _('revision(s) to rewrite'))],
     _('hg qundrift [ -a | -r REV | -r REV:REV ]'))
}
