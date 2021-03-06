import unittest
import mock
import os
import shutil
import tempfile

import kojihub



class TestImportImageInternal(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    @mock.patch('koji.pathinfo.work')
    @mock.patch('kojihub.import_archive')
    @mock.patch('kojihub.get_archive_type')
    @mock.patch('kojihub.get_build')
    @mock.patch('kojihub.Task')
    @mock.patch('kojihub.context')
    def test_basic(self, context, Task, get_build, get_archive_type, import_archive, work):
        imgdata = {
            'arch': 'x86_64',
            'task_id': 1,
            'files': [
                'some_file',
            ],
            'rpmlist': [
            ],
        }
        cursor = mock.MagicMock()
        context.cnx.cursor.return_value = cursor
        context.session.host_id = 42
        get_build.return_value = {
            'id': 2,
        }
        get_archive_type.return_value = 4
        work.return_value = self.tempdir
        os.makedirs(self.tempdir + "/tasks/1/1")
        kojihub.importImageInternal(task_id=1, build_id=2, imgdata=imgdata)

    @mock.patch('kojihub.get_rpm')
    @mock.patch('koji.pathinfo.build')
    @mock.patch('koji.pathinfo.work')
    @mock.patch('kojihub.import_archive')
    @mock.patch('kojihub.get_archive_type')
    @mock.patch('kojihub.get_build')
    @mock.patch('kojihub.Task')
    @mock.patch('kojihub.context')
    def test_with_rpm(self, context, Task, get_build, get_archive_type, import_archive, build, work, get_rpm):
        rpm = {
            #'location': 'foo',
            'id': 6,
            'name': 'foo',
            'version': '3.1',
            'release': '2',
            'epoch': 0,
            'arch': 'noarch',
            'payloadhash': 'laksjdflkasjdf',
            'size': 42,
            'buildtime': 12345,
        }
        imgdata = {
            'arch': 'x86_64',
            'task_id': 1,
            'files': [
                'some_file',
            ],
            'rpmlist': [rpm],
        }
        cursor = mock.MagicMock()
        context.cnx.cursor.return_value = cursor
        context.session.host_id = 42
        get_build.return_value = {'id': 2 }
        get_rpm.return_value = rpm
        get_archive_type.return_value = 4
        work.return_value = self.tempdir
        build.return_value = self.tempdir
        import_archive.return_value = {
            'id': 9,
            'filename': self.tempdir + '/foo.archive',
        }
        workdir = self.tempdir + "/tasks/1/1"
        os.makedirs(workdir)
        # Create a log file to exercise that code path
        with open(workdir + '/foo.log', 'w'):
            pass

        kojihub.importImageInternal(task_id=1, build_id=2, imgdata=imgdata)

        # Check that the log symlink made it to where it was supposed to.
        dest = os.readlink(workdir + '/foo.log')
        self.assertEquals(dest, self.tempdir + '/data/logs/image/foo.log')

        # And.. check all the sql statements
        self.assertEquals(len(cursor.execute.mock_calls), 1)
        expression, kwargs = cursor.execute.mock_calls[0][1]
        expression = " ".join(expression.split())
        expected = 'INSERT INTO image_listing (image_id,rpm_id) ' + \
            'VALUES (%(image_id)i,%(rpm_id)i)'
        self.assertEquals(expression, expected)
        self.assertEquals(kwargs, {'image_id': 9, 'rpm_id': 6})
