from taggit.managers import TaggableManager, _TaggableManager
from taggit.utils import require_instance_manager

import django.dispatch

post_tagging = django.dispatch.Signal(providing_args=["category", "tags"])
post_untagging = django.dispatch.Signal(providing_args=["category", "tags"])

class TopicableManager(TaggableManager):

    def __get__(self, instance, model):
        if instance is not None and instance.pk is None:
            raise ValueError("%s objects need to have a primary key value "
                             "before you can access their tags." % model.__name__)
        manager = _TopicableManager(
            through=self.through, model=model, instance=instance
        )
        return manager

class _TopicableManager(_TaggableManager):

    @require_instance_manager
    def topics(self):
        return self.through.objects.filter(
            content_object= self.instance
        )

    @require_instance_manager
    def add(self, *tags, **extra_kwargs):

        # TODO check below how to check only once that "category" is among
        # the passed arguments (otherwise return...)

        if not tags:
            kwargs = self._lookup_kwargs()
            kwargs.update(extra_kwargs)

            # continuing without a category, will cause an exception
            if "category" not in kwargs:
                return

            self.through.objects.get_or_create(**kwargs)
        else:
        
            # continuing without a category, will cause an exception
            if "category" not in extra_kwargs:
                return
        
            super(_TopicableManager, self).add(*tags, **extra_kwargs)

        # call custom Signal
        post_tagging.send(sender=self.through, category=extra_kwargs.get('category'), tags=tags)

    @require_instance_manager
    def remove(self, *tags, **extra_kwargs):
        if not tags:
            kwargs = self._lookup_kwargs()
            kwargs.update(extra_kwargs)
            self.through.objects.filter(**kwargs).delete()
        else:
            super(_TopicableManager, self).remove(*tags, **extra_kwargs)

        # call custom Signal
        post_untagging.send(sender=self.through, category=extra_kwargs.get('category'), tags=tags)


    @require_instance_manager
    def clear(self):
        taggings = self.through.objects.filter(**self._lookup_kwargs())
        # collect all tags in categories
        categorized_tags = {}
        for tagging in taggings:
            if not categorized_tags.has_key(tagging.category):
                categorized_tags[tagging.category] = []
            if tagging.tag:
                categorized_tags[tagging.category].append(tagging.tag)
        # delete all taggings
        taggings.delete()
        # call custom Signal foreach category
        for cat in categorized_tags.keys():
            post_untagging.send(sender=self.through, category=cat, tags=categorized_tags.get(cat))


