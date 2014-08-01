tl;dr: If you're happy with GFK-based tagging, then move along, there's
nothing for you to see here.

The basics are almost trivial: tagging done by a M2M relationship between
a table of tags (model SaneTag) and a tagged model.  Without any of the
syntactic sugar or conveniences, all you need is that table of tags and
something like

    tags = ManyToManyField('MyTagModel')

in each model that needs to be tagged.  For a pretty common case, where
you're mainly concerned about a per-model tagging context, this pretty much
works already, though there's plenty of room for adding conveniences.  And
if you do often need cross-model tags - say, eg., you have separate models
for television shows and movies, but sometimes want to find instances of both
types based on the tagging, that's only a little more work, which is to say
further opportunities for adding convenient interfaces.

This code is currently a very early and incomplete draft of some ideas I've
been kicking around for years.  Turning those musings into this sketch grew
out of discussion in #django-south that went rather beyond the initial
difficulty in making some specific migration work.
