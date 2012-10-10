from __future__ import absolute_import

import datetime

from django.conf import settings
from django.db import backend, transaction, DEFAULT_DB_ALIAS, models
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature

from .models import (Book, Award, AwardNote, Person, Child, Toy, PlayedWith,
    PlayedWithNote, Email, Researcher, Food, Eaten, Policy, Version, Location,
    Item, Image, File, Photo, FooFile, FooImage, FooPhoto, FooFileProxy)


# Can't run this test under SQLite, because you can't
# get two connections to an in-memory database.
class DeleteLockingTest(TransactionTestCase):
    def setUp(self):
        # Create a second connection to the default database
        conn_settings = settings.DATABASES[DEFAULT_DB_ALIAS]
        self.conn2 = backend.DatabaseWrapper({
            'HOST': conn_settings['HOST'],
            'NAME': conn_settings['NAME'],
            'OPTIONS': conn_settings['OPTIONS'],
            'PASSWORD': conn_settings['PASSWORD'],
            'PORT': conn_settings['PORT'],
            'USER': conn_settings['USER'],
            'TIME_ZONE': settings.TIME_ZONE,
        })

        # Put both DB connections into managed transaction mode
        transaction.enter_transaction_management()
        transaction.managed(True)
        self.conn2._enter_transaction_management(True)

    def tearDown(self):
        # Close down the second connection.
        transaction.leave_transaction_management()
        self.conn2.close()

    @skipUnlessDBFeature('test_db_allows_multiple_connections')
    def test_concurrent_delete(self):
        "Deletes on concurrent transactions don't collide and lock the database. Regression for #9479"

        # Create some dummy data
        b1 = Book(id=1, pagecount=100)
        b2 = Book(id=2, pagecount=200)
        b3 = Book(id=3, pagecount=300)
        b1.save()
        b2.save()
        b3.save()

        transaction.commit()

        self.assertEqual(3, Book.objects.count())

        # Delete something using connection 2.
        cursor2 = self.conn2.cursor()
        cursor2.execute('DELETE from delete_regress_book WHERE id=1')
        self.conn2._commit()

        # Now perform a queryset delete that covers the object
        # deleted in connection 2. This causes an infinite loop
        # under MySQL InnoDB unless we keep track of already
        # deleted objects.
        Book.objects.filter(pagecount__lt=250).delete()
        transaction.commit()
        self.assertEqual(1, Book.objects.count())
        transaction.commit()


class DeleteCascadeTests(TestCase):
    def test_generic_relation_cascade(self):
        """
        Django cascades deletes through generic-related objects to their
        reverse relations.

        """
        person = Person.objects.create(name='Nelson Mandela')
        award = Award.objects.create(name='Nobel', content_object=person)
        note = AwardNote.objects.create(note='a peace prize',
                                        award=award)
        self.assertEqual(AwardNote.objects.count(), 1)
        person.delete()
        self.assertEqual(Award.objects.count(), 0)
        # first two asserts are just sanity checks, this is the kicker:
        self.assertEqual(AwardNote.objects.count(), 0)

    def test_fk_to_m2m_through(self):
        """
        If an M2M relationship has an explicitly-specified through model, and
        some other model has an FK to that through model, deletion is cascaded
        from one of the participants in the M2M, to the through model, to its
        related model.

        """
        juan = Child.objects.create(name='Juan')
        paints = Toy.objects.create(name='Paints')
        played = PlayedWith.objects.create(child=juan, toy=paints,
                                           date=datetime.date.today())
        note = PlayedWithNote.objects.create(played=played,
                                             note='the next Jackson Pollock')
        self.assertEqual(PlayedWithNote.objects.count(), 1)
        paints.delete()
        self.assertEqual(PlayedWith.objects.count(), 0)
        # first two asserts just sanity checks, this is the kicker:
        self.assertEqual(PlayedWithNote.objects.count(), 0)

    def test_15776(self):
        policy = Policy.objects.create(pk=1, policy_number="1234")
        version = Version.objects.create(policy=policy)
        location = Location.objects.create(version=version)
        item = Item.objects.create(version=version, location=location)
        policy.delete()


class DeleteCascadeTransactionTests(TransactionTestCase):
    def test_inheritance(self):
        """
        Auto-created many-to-many through tables referencing a parent model are
        correctly found by the delete cascade when a child of that parent is
        deleted.

        Refs #14896.
        """
        r = Researcher.objects.create()
        email = Email.objects.create(
            label="office-email", email_address="carl@science.edu"
        )
        r.contacts.add(email)

        email.delete()

    def test_to_field(self):
        """
        Cascade deletion works with ForeignKey.to_field set to non-PK.

        """
        apple = Food.objects.create(name="apple")
        eaten = Eaten.objects.create(food=apple, meal="lunch")

        apple.delete()
        self.assertFalse(Food.objects.exists())
        self.assertFalse(Eaten.objects.exists())


class LargeDeleteTests(TestCase):
    def test_large_deletes(self):
        "Regression for #13309 -- if the number of objects > chunk size, deletion still occurs"
        for x in range(300):
            track = Book.objects.create(pagecount=x+100)
        # attach a signal to make sure we will not fast-delete
        def noop(*args, **kwargs):
            pass
        models.signals.post_delete.connect(noop, sender=Book)
        Book.objects.all().delete()
        models.signals.post_delete.disconnect(noop, sender=Book)
        self.assertEqual(Book.objects.count(), 0)


class ProxyDeleteTest(TestCase):
    """
    Tests on_delete behavior for proxy models.

    See #16128.

    """
    def create_image(self):
        """Return an Image referenced by both a FooImage and a FooFile."""
        # Create an Image
        test_image = Image()
        test_image.save()
        foo_image = FooImage(my_image=test_image)
        foo_image.save()

        # Get the Image instance as a File
        test_file = File.objects.get(pk=test_image.pk)
        foo_file = FooFile(my_file=test_file)
        foo_file.save()

        return test_image


    def test_delete_proxy(self):
        """
        Deleting the *proxy* instance bubbles through to its non-proxy and
        *all* referring objects are deleted.

        """
        self.create_image()

        Image.objects.all().delete()

        # An Image deletion == File deletion
        self.assertEqual(len(Image.objects.all()), 0)
        self.assertEqual(len(File.objects.all()), 0)

        # The Image deletion cascaded and *all* references to it are deleted.
        self.assertEqual(len(FooImage.objects.all()), 0)
        self.assertEqual(len(FooFile.objects.all()), 0)


    def test_delete_proxy_of_proxy(self):
        """
        Deleting a proxy-of-proxy instance should bubble through to its proxy
        and non-proxy parents, deleting *all* referring objects.

        """
        test_image = self.create_image()

        # Get the Image as a Photo
        test_photo = Photo.objects.get(pk=test_image.pk)
        foo_photo = FooPhoto(my_photo=test_photo)
        foo_photo.save()

        Photo.objects.all().delete()

        # A Photo deletion == Image deletion == File deletion
        self.assertEqual(len(Photo.objects.all()), 0)
        self.assertEqual(len(Image.objects.all()), 0)
        self.assertEqual(len(File.objects.all()), 0)

        # The Photo deletion should have cascaded and deleted *all*
        # references to it.
        self.assertEqual(len(FooPhoto.objects.all()), 0)
        self.assertEqual(len(FooFile.objects.all()), 0)
        self.assertEqual(len(FooImage.objects.all()), 0)


    def test_delete_concrete_parent(self):
        """
        Deleting an instance of a concrete model should also delete objects
        referencing its proxy subclass.

        """
        self.create_image()

        File.objects.all().delete()

        # A File deletion == Image deletion
        self.assertEqual(len(File.objects.all()), 0)
        self.assertEqual(len(Image.objects.all()), 0)

        # The File deletion should have cascaded and deleted *all* references
        # to it.
        self.assertEqual(len(FooFile.objects.all()), 0)
        self.assertEqual(len(FooImage.objects.all()), 0)


    def test_delete_proxy_pair(self):
        """
        If a pair of proxy models are linked by an FK from one concrete parent
        to the other, deleting one proxy model cascade-deletes the other, and
        the deletion happens in the right order (not triggering an
        IntegrityError on databases unable to defer integrity checks).

        Refs #17918.

        """
        # Create an Image (proxy of File) and FooFileProxy (proxy of FooFile,
        # which has an FK to File)
        image = Image.objects.create()
        as_file = File.objects.get(pk=image.pk)
        FooFileProxy.objects.create(my_file=as_file)

        Image.objects.all().delete()

        self.assertEqual(len(FooFileProxy.objects.all()), 0)