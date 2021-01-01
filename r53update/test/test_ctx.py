#!/bin/env python
# -*- coding: utf-8 -*-
#
# R53Update Dynamic DNS Updater
# (C)2014 Takuya Sawada All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# 
from ..r53update import R53UpdateApp
from pyfakefs import fake_filesystem_unittest

import botocore
import string
import random
import mock
import os

class TestAppContext(fake_filesystem_unittest.TestCase):
	def setUp(self):
		# setup fakefs
		self.setUpPyfakefs()

		# key-pair test data
		self.profile = {
			'env': (self.randomstr(20), self.randomstr(40)),
			'default': (self.randomstr(20), self.randomstr(40)),
			'test': (self.randomstr(20), self.randomstr(40))
		}

		# mount botocore packages directory for some resources
		self.fs.add_real_directory(os.path.dirname(botocore.__file__))

		# create virtual file
		self.fs.CreateFile(os.path.expanduser('~/.aws/config'))
		self.assertTrue(os.path.isfile(os.path.expanduser('~/.aws/config')))

		# initialize aws config
		with open(os.path.expanduser('~/.aws/config'), 'wt') as config:
			config.write(
				u"[default]\n"
				u"aws_access_key_id = %s\n"
				u"aws_secret_access_key =  %s\n"
				u"region = ap-northeast-1\n"
				u"output = json\n"
				u"\n"
				u"[profile test]\n"
				u"aws_access_key_id = %s\n"
				u"aws_secret_access_key =  %s\n"
				u"region = ap-northeast-2\n"
				u"output = json\n"

				% (self.profile['default'] + self.profile['test'])
			)

	def randomstr(self, length):
		return ''.join([random.choice(string.digits + string.ascii_uppercase) for i in range(12)])

	# check credential with environment variable
	def test_env(self):
		AWS_ACCESS_KEY, AWS_SECRET_KEY = self.profile['env']

		ENV = {
			'AWS_ACCESS_KEY_ID': AWS_ACCESS_KEY,
			'AWS_SECRET_ACCESS_KEY': AWS_SECRET_KEY
		}

		with mock.patch.dict('os.environ', ENV):
			ctx = R53UpdateApp.Context()

			creds = ctx.session.get_credentials()
			self.assertNotEqual(creds, None)

			self.assertEqual(creds.access_key, AWS_ACCESS_KEY)
			self.assertEqual(creds.secret_key, AWS_SECRET_KEY)

			self.assertNotEqual(ctx.getR53Client(), None)

	# check credential with profile [default] (implicit)
	def test_profile_default_implicit(self):
		AWS_ACCESS_KEY, AWS_SECRET_KEY = self.profile['default']
		ctx = R53UpdateApp.Context()

		creds = ctx.session.get_credentials()
		self.assertNotEqual(creds, None)

		self.assertEqual(creds.access_key, AWS_ACCESS_KEY)
		self.assertEqual(creds.secret_key, AWS_SECRET_KEY)

		self.assertNotEqual(ctx.getR53Client(), None)
			
	# check credential with profile [default] (explicit)
	def test_profile_default_explicit(self):
		AWS_ACCESS_KEY, AWS_SECRET_KEY = self.profile['default']
		ctx = R53UpdateApp.Context('default')

		creds = ctx.session.get_credentials()
		self.assertEqual(creds.access_key, AWS_ACCESS_KEY)
		self.assertEqual(creds.secret_key, AWS_SECRET_KEY)

		self.assertNotEqual(ctx.getR53Client(), None)

	# check credential with profile [test]
	def test_profile_test(self):
		AWS_ACCESS_KEY, AWS_SECRET_KEY = self.profile['test']
		ctx = R53UpdateApp.Context('test')

		creds = ctx.session.get_credentials()
		self.assertEqual(creds.access_key, AWS_ACCESS_KEY)
		self.assertEqual(creds.secret_key, AWS_SECRET_KEY)

		self.assertNotEqual(ctx.getR53Client(), None)

	# check not exist profile cause `ProfileNotFound` exception
	def test_profile_not_found(self):
		with self.assertRaises(botocore.exceptions.ProfileNotFound):
			ctx = R53UpdateApp.Context('notexist')
			ctx.getR53Client()

