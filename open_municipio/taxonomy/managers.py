from taggit.managers import TaggableManager, _TaggableManager
from taggit.utils import require_instance_manager

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
        if not tags:
            kwargs = self._lookup_kwargs()
            kwargs.update(extra_kwargs)
            self.through.objects.get_or_create(**kwargs)
        else:
            super(_TopicableManager, self).add(*tags, **extra_kwargs)

