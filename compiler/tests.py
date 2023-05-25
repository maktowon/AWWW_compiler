import datetime

from django.test import TestCase
from .views import *
from django.test import RequestFactory, Client
from django.urls import reverse
from .forms import DirectoryForm, FileForm
from django.template.loader import render_to_string


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
    def setUp(self):
        user = new_user()
        dir1 = Directory.objects.create(name="dir1", owner=user)
        dir2 = Directory.objects.create(name="dir2", parent=dir1, owner=user)
        File.objects.create(name="outer", parent=dir1, owner=user)
        File.objects.create(name="inner", parent=dir2, owner=user)

    def test_complex_delete(self):
        dir1 = Directory.objects.get(id=1)
        dir1.set_folder_inactive()

        dir2 = Directory.objects.get(id=2)
        f1 = File.objects.get(id=1)
        f2 = File.objects.get(id=2)
        self.assertFalse(dir1.active)
        self.assertFalse(dir2.active)
        self.assertFalse(f1.active)
        self.assertFalse(f2.active)


class DirectoryFormTestCase(TestCase):
    def setUp(self):
        self.user = new_user()
        self.data = {'name': 'Test Directory', 'description': 'Test Description'}

    def test_directory_form_valid(self):
        form = DirectoryForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_directory_form_invalid(self):
        invalid_data = {'name': '', 'description': 'Test Description'}
        form = DirectoryForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_directory_form_save(self):
        form = DirectoryForm(data=self.data)
        self.assertTrue(form.is_valid())
        directory = form.save(commit=False)
        directory.owner = self.user
        directory.save()
        self.assertEqual(Directory.objects.count(), 1)
        self.assertEqual(directory.name, 'Test Directory')
        self.assertEqual(directory.description, 'Test Description')
        self.assertEqual(directory.owner, self.user)


class FileFormTestCase(TestCase):
    def setUp(self):
        self.user = new_user()
        self.directory = Directory.objects.create(name='Test Directory', owner=self.user)
        self.data = {'name': 'Test File', 'description': 'Test Description'}

    def test_file_form_valid(self):
        form = FileForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_file_form_invalid(self):
        invalid_data = {'name': '', 'description': 'Test Description'}
        form = FileForm(data=invalid_data)
        self.assertFalse(form.is_valid())

    def test_file_form_save(self):
        form = FileForm(data=self.data)
        self.assertTrue(form.is_valid())
        file = form.save(commit=False)
        file.owner = self.user
        file.parent = self.directory
        file.save()
        self.assertEqual(File.objects.count(), 1)
        self.assertEqual(file.name, 'Test File')
        self.assertEqual(file.description, 'Test Description')
        self.assertEqual(file.owner, self.user)
        self.assertEqual(file.parent, self.directory)

# TODO testowanie views
class CompilerViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compiler/register.html')

        response = self.client.post(reverse('register'), data={'username': 'newuser', 'password1': 'newpassword', 'password2': 'newpassword'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertRedirects(response, reverse('login_to'))

    def test_login_view(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compiler/login.html')

        response = self.client.post(reverse('login'), data={'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertRedirects(response, reverse('home'))

    def test_logout_view(self):
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertRedirects(response, reverse('login'))

    def test_folder_details_view(self):
        folder = Directory.objects.create(name='Test Folder', owner=self.user)
        response = self.client.get(reverse('folder_details', args=[folder.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compiler/folder_details.html')

    def test_root_folder_view(self):
        response = self.client.get(reverse('root_folder'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compiler/root_folder.html')

    def test_folder_delete_view(self):
        folder = Directory.objects.create(name='Test Folder', owner=self.user)
        response = self.client.get(reverse('folder_delete', args=[folder.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertRedirects(response, reverse('home'))

    def test_file_delete_view(self):
        file = File.objects.create(name='test.c', owner=self.user)
        response = self.client.get(reverse('file_delete', args=[file.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after delete
        self.assertRedirects(response, reverse('home'))

    def test_run_view(self):
        response = self.client.post(reverse('home'), data={'codearea': 'int main() { return 0; }', 'standard': 'c89', 'optimizations': 'O1', 'processor': 'mcs51', 'MCSoption': 'small', 'STM8option': '', 'Z80option': '', 'file_id': ''})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'asm': '', 'error': ''})

    def test_edit_sections_view(self):
        response = self.client.get(reverse('edit_sections'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'compiler/edit_sections.html')