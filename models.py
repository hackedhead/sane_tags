from __future__ import absolute_import

from django.db import connection
from django.db.models import CharField, Model, TextField


class SaneTag(Model):

    ### Fields and other normal Django parts ###

    name = CharField(max_length=40)
    namei = CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name

    ### FIX ME ### I guess there IS no way to always get this sort of thing done
    ###            in Django - bulk inserts and updates never come near model methods.
    ###            It's really a job for the backend; a trigger to make the
    ###            case-folded copy, or better still a case-blind index.
    ### UNFIXABLE ### in general

    def save(self, *args, **kwargs):
        self.namei = self.name.lower()
        super(SaneTag, self).save(*args, **kwargs)

    ### SaneTag API methods ###

    def get_all_linked_keys(self):
        """returns the keys of all instances that are linked to this tag

        -> {model_class:[key, ...], ...}
        """

        return self._get_all_linked_keys_of(self._get_all_m2m())

    def get_all_linked_keys_of(self, model_list):
        """returns the keys of all instances of models in list which are linked to this tag

        -> {model_class:[key, ...], ...}, raises ValueError if any models not valid m2m
        """

        return self._get_all_linked_keys_of(self._m2m_from_models(model_list))

    ToDo = """
    count is actually a little different.  a total summary count is one thing that's
    more expensive than with generic relations, but is arguably more likely to be used
    than the broken-down counts.  Maybe?

    sane_tag.model_name_set.count()

    def    SaneTag.count_all() -> {model_class:count,...}
    def    SaneTag.count_all_of([model_class,...]) - {model_class:count,...}


    def    SaneTag.get_ids({tag,...}) -> {tag_id,...}

    def    SaneTag.get_linked_keys({tag,...}) -> {model_class:{key,...},...}

    def    SaneTag.get_tag_cloud_for(model_instance) -> [(count, sane_tag), ...]

"""

    ### Internal implementation methods ###

    @classmethod
    def _get_all_m2m(self):
        """returns a ro_dict describing all m2m relations to SaneTag
        -> {model_class: related_object}
        """

        related_objects = [x[0] for x in self._meta.get_all_related_m2m_objects_with_model()]
        return dict((ro.model, ro) for ro in related_objects)

    @classmethod
    def _m2m_from_models(self, model_list):
        """returns an ro_dict describing all the models in model_list
        -> {model_class: related_object} for all models in model_list
        RAISES ValueError if any of model_list are not found in m2m relations
        """

        ro_dict = self._get_all_m2m()
        try:
            model_ro = [(mc, ro_dict[mc]) for mc in model_list]
        except KeyError:
            raise ValueError("model_list item has no m2m: %s" % mc)
        return dict(model_ro)

    @staticmethod
    def _m2m_from_ro(ro):
        """returns info about m2m relation extracted from ro
        -> (m2m_table_name, sane_tag_id_name, other_id_name)
        """

        rof = ro.field
        return (rof.m2m_db_table(), rof.m2m_reverse_name(), rof.m2m_column_name())

    def _get_all_linked_keys_of(self, ro_dict):
        """returns all the keys of instances of given m2m models which are linked to this tag
        -> {model_class:[key, ...], ...}
        """

        res = {}
        with connection.cursor() as cursor:
            for model_class,ro in ro_dict.items():
                m2m_table,tags_id,tagged_id = self._m2m_from_ro(ro)
                cursor.execute(
                    "SELECT %s FROM %s WHERE %s = %%s" % (tagged_id, m2m_table, tags_id),
                    [self.id])
                res[model_class] = [row[0] for row in cursor.fetchall()]

        return res

    def _get_all_counts_of(self, ro_dict):
        """returns the number of instances of given m2m models which are linked to this tag
        -> {model_class:count, ...}
        """

        res = {}
        with connection.cursor() as cursor:
            for model_class,ro in ro_dict.items():
                m2m_table,tags_id,tagged_id = self._m2m_from_ro(ro)
                cursor.execute(
                    "SELECT COUNT(*) FROM %s WHERE %s = %%s" % (m2m_table, tags_id),
                    [self_id])
                res[model_class] = [row[0] for row in cursor.fetchall()]

        return res

    @classmethod
    def _get_all_cotagged(self, the_thing):
        """returns [(thing_id, tag_id)...] for all tags of all things which share one or
        more tags with the_thing.

        EXPERIMENTAL, want to record the query plan while it's fresh in mind

        This is fancy cloud taggish and/or for similarity by tags.
        """

        thing_class = the_thing.__class__
        the_ro = self._m2m_from_models([thing_class])[thing_class]
        names = dict(zip(('table', 'tagid', 'thingid'), self._m2m_from_ro(the_ro)))
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT %(thingid)s,%(tagid)s FROM %(table)s WHERE %(thingid)s IN
                (SELECT DISTINCT t1.%(thingid)s FROM %(table)s as t1 WHERE t1.%(tagid)s IN
                (SELECT t2.%(tagid)s FROM %(table)s as t2 WHERE t2.%(thingid)s = %%s))""" % names,
                [the_thing.pk])
            res = cursor.fetchall()

        return res
