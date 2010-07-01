# qfixdrift.py - refresh applied patches in mq patch queue
#
# Copyright 2009 L. David Baron <dbaron@dbaron.org> (and contributors to
# mq.py, from which a few pieces were taken)
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2, incorporated herein by reference.
#
# This version is compatible with Mercurial 1.6.

'''clean up patch drift in an mq patch queue

This extension will rewrite applied patches in an mq patch queue to
match the diff as they are currently applied.  In other words, it
updates the applied patches so that they will re-apply without fuzz or
line offsets.

It provides a single command: qfixdrift
'''

from mercurial.i18n import _
from mercurial.node import hex, short
from mercurial import util, cmdutil
from hgext.mq import patchheader

def qfixdrift(ui, repo, *args, **opts):
    """rewrite given patches to clean up patch drift

    Rewrite the specified patches so their diff matches the context in
    which they are currently applied.

    The patches to rewrite must be specified with -a or -r:

     * with -a, all applied patches are rewritten

     * with -r, the given revisions (which must be applied mq patches)
       are rewritten
    """
    applied = opts.get('applied')
    rev = opts.get('rev')
    if applied:
        if rev:
            raise util.Abort(_("qfixdrift requires only one of -a or -r"))
        patches = repo.mq.applied
    else:
        if not rev:
            raise util.Abort(_("qfixdrift requires either -a or -r"))
        def patch_for_rev(r):
            for qp in repo.mq.applied:
                # qp.node is the binary hash and r is an integer
                if qp.node == repo.changelog.node(r):
                    return qp
            raise util.Abort(_("revision %s is not an applied mq patch") %
                             short(repo.changelog.node(r)))
        patches = map(patch_for_rev, cmdutil.revrange(repo, rev))
    for p in patches:
        if p.name == ".hg.patches.merge.marker":
            continue
        repo.ui.write(_("updating patch %s\n") % p.name)
        ph = patchheader(repo.mq.join(p.name))
        patchf = repo.mq.opener(p.name, 'w')
        comments = str(ph)
        if comments:
            patchf.write(comments)
        repo.mq.printdiff(repo=repo,
                          diffopts=repo.mq.diffopts(patchfn=p.name),
                          node1=repo.mq.qparents(repo, p.node),
                          node2=hex(p.node),
                          fp=patchf)
        patchf.close()

cmdtable = {
    "qfixdrift":
    (qfixdrift,
     [('a', 'applied', None, _('rewrite all applied patches')),
      ('r', 'rev', [], _('revision(s) to rewrite'))],
     _('hg qfixdrift [ -a | -r REV | -r REV:REV ]'))
}
