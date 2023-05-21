import datetime

from django.test import TestCase
from .views import *


def new_user():
    return User.objects.create_user("test", password="testowe12345")


class DirectoryTest(TestCase):
    def setUp(self):
        user = new_user()
        dir1 = Directory.objects.create(name="Dir1", owner=user)
        Directory.objects.create(name="Dir2", parent=dir1, owner=user)
        Directory.objects.create(name="Dir3", description="test desc", owner=user)

    def test_creation(self):
        dir1 = Directory.objects.get(id=1)
        dir3 = Directory.objects.get(id=3)

        self.assertEquals(dir1.name, "Dir1")
        self.assertEquals(dir1.creation_date, datetime.date.today())
        self.assertEquals(dir1.modified_date, datetime.date.today())
        self.assertEquals(dir1.owner, User.objects.get(id=1))
        self.assertEquals(dir1.description, "")
        self.assertEquals(dir3.description, "test desc")

    def test_is_root(self):
        dir1 = Directory.objects.get(id=1)
        dir3 = Directory.objects.get(id=3)

        self.assertEquals(dir1.parent, None)
        self.assertEquals(dir3.parent, None)

    def test_parentness(self):
        dir1 = Directory.objects.get(id=1)
        dir2 = Directory.objects.get(id=2)
        dir3 = Directory.objects.get(id=3)

        self.assertTrue(dir2 in dir1.directory_set.all())
        self.assertFalse(dir3 in dir1.directory_set.all())
        self.assertEquals(dir2.parent, dir1)

    def test_basic_deactivation(self):
        dir3 = Directory.objects.get(id=3)
        self.assertTrue(dir3.active)

        dir3.set_folder_inactive()
        self.assertIs(dir3.active, False)

    def test_parent_deactivation(self):
        dir1 = Directory.objects.get(id=1)
        self.assertTrue(dir1.active)
        dir2 = Directory.objects.get(id=2)
        self.assertTrue(dir2.active)

        dir1.set_folder_inactive()
        dir2 = Directory.objects.get(id=2)
        self.assertFalse(dir1.active)
        self.assertFalse(dir2.active)

    def test_directory_delete(self):
        dir1 = Directory.objects.get(id=1)
        Directory.objects.get(id=2)
        dir1.delete()
        try:
            Directory.objects.get(id=1)
            self.fail("parent folder deletion failed")
        except ObjectDoesNotExist:
            pass
        try:
            Directory.objects.get(id=2)
            self.fail("subfolder deletion failed")
        except ObjectDoesNotExist:
            pass
        Directory.objects.get(id=3)

    def test_user_delete(self):
        Directory.objects.get(id=3)
        Directory.objects.get(id=1)
        User.objects.get(id=1).delete()
        try:
            Directory.objects.get(id=1)
            self.fail("folder didnt delete after user deletion")
        except ObjectDoesNotExist:
            pass
        try:
            Directory.objects.get(id=2)
            self.fail("folder didnt delete after user deletion")
        except ObjectDoesNotExist:
            pass
        try:
            Directory.objects.get(id=3)
            self.fail("folder didnt delete after user deletion")
        except ObjectDoesNotExist:
            pass


class FileTest(TestCase):
    def setUp(self):
        user = new_user()
        File.objects.create(name="f1", description="some desc", owner=user)
        File.objects.create(name="f2", code="some code", owner=user)

    def test_creation(self):
        f1 = File.objects.get(id=1)
        f2 = File.objects.get(id=2)
        self.assertEquals(f1.name, "f1")
        self.assertEquals(f1.creation_date, datetime.date.today())
        self.assertEquals(f1.modified_date, datetime.date.today())
        self.assertEquals(f1.description, "some desc")
        self.assertEquals(f2.description, "")
        self.assertEquals(f1.code, "// type your code here")
        self.assertEquals(f2.code, "some code")
        self.assertEquals(f1.owner, User.objects.get(id=1))

    def test_is_root(self):
        f1 = File.objects.get(id=1)
        f2 = File.objects.get(id=2)
        self.assertEquals(f1.parent, None)
        self.assertEquals(f2.parent, None)

    def test_file_delete(self):
        File.objects.get(id=1).delete()
        try:
            File.objects.get(id=1)
            self.fail("file didnt delete itself")
        except ObjectDoesNotExist:
            pass
        File.objects.get(id=2)

    def test_user_delete(self):
        File.objects.get(id=1)
        File.objects.get(id=2)
        User.objects.get(id=1).delete()
        try:
            File.objects.get(id=1)
            self.fail("file didnt delete after user deletion")
        except ObjectDoesNotExist:
            pass
        try:
            File.objects.get(id=2)
            self.fail("file didnt delete after user deletion")
        except File.DoesNotExist:
            pass


class DirectoryAndFileTest(TestCase):
    pass

