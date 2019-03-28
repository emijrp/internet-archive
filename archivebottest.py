import archivebot
import collections
import contextlib
import io
import re


class SwallowArgInit:
	def __init__(self, *args, **kwargs):
		pass


class PageCatalogue:
	def __init__(self):
		self._pages = {}
		self.pageCls = None

	def add_page(self, page):
		self._pages[page.title()] = page

	def get_page(self, title):
		if title in self._pages:
			return self._pages[title]
		return self.pageCls.make(title, None, exists = False)


# Mock objects
class MockSite(SwallowArgInit):
	pass

class MockCategory(SwallowArgInit):
	pass

class MockCategorizedPageGenerator(SwallowArgInit):
	pass

def make_preloading_generator(catalogue, titles):
	def gen(*args, **kwargs):
		for title in titles:
			yield catalogue.get_page(title)
	return gen

def make_mock_page(catalogue):
	class MockPage:
		def __new__(cls, *args, **kwargs):
			if len(args) >= 2 and type(args[0]) is MockSite:
				return catalogue.get_page(args[1])
			return super().__new__(cls, *args, **kwargs)

		@classmethod
		def make(cls, title, text, exists = True):
			obj = cls()
			obj._title = title
			obj.text = text
			obj._exists = exists
			obj.savecomment = None
			return obj

		def title(self):
			return self._title

		def exists(self):
			return self._exists

		def save(self, comment):
			self.savecomment = comment
	return MockPage


# Mock modules
class MockPywikibotModule:
	Site = MockSite
	Category = MockCategory
	Page = None

	def showDiff(*args, **kwargs):
		pass

class MockPagegeneratorsModule:
	CategorizedPageGenerator = MockCategorizedPageGenerator
	PreloadingGenerator = None


# Mock ArchiveBot viewer method
def make_getArchiveBotViewer(viewerData):
	def getArchiveBotViewer(url):
		if url in viewerData:
			return viewerData[url]
		return False, 'https://archive.fart.website/archivebot/viewer/', '', 0
	return getArchiveBotViewer


@contextlib.contextmanager
def mock(titles, viewerData):
	origPywikibot = archivebot.pywikibot
	archivebot.pywikibot = MockPywikibotModule
	origPagegenerators = archivebot.pagegenerators
	archivebot.pagegenerators = MockPagegeneratorsModule

	catalogue = PageCatalogue()
	MockPywikibotModule.Page = make_mock_page(catalogue)
	catalogue.pageCls = MockPywikibotModule.Page
	MockPagegeneratorsModule.PreloadingGenerator = make_preloading_generator(catalogue, titles)

	origGetarchivebotviewer = archivebot.getArchiveBotViewer
	archivebot.getArchiveBotViewer = make_getArchiveBotViewer(viewerData) # NB, this is actually mocking archiveteamfun.getArchiveBotViewer

	yield catalogue, MockPywikibotModule.Page

	archivebot.pywikibot = origPywikibot
	archivebot.pagegenerators = origPagegenerators
	archivebot.getArchiveBotViewer = origGetarchivebotviewer


# Container for the test page information
# textafter can be None, which means that the text should remain unchanged
# textafterpatterns, if not None, contains regex patterns which must match lines in the text in the order specified
# savecomment being None means that the page wasn't saved (e.g. no changes needed)
TestPage = collections.namedtuple('TestPage', ('title', 'textbefore', 'textafter', 'textafterpatterns', 'savecomment'))


def test_main():
	pagesData = [
		TestPage(title = 'ArchiveBot/Simple/list', textbefore = '\n'.join(['https://example.org/']), textafter = None, textafterpatterns = None, savecomment = None),
		TestPage(
		  title = 'ArchiveBot/Simple',
		  textbefore = '<!-- bot --><!-- /bot -->',
		  textafter = None,
		  textafterpatterns = ['^<!-- bot -->$', 'Statistics', 'Do not edit', r'example\.org.*\{\{notsaved\}\}', '^<!-- /bot -->$'],
		  savecomment = 'BOT - Updating page: {{saved}} (0), {{notsaved}} (1), Total size (0&nbsp;KiB)',
		 ),

		TestPage(
		  title = 'ArchiveBot/Sorting/list',
		  textbefore = '\n'.join(['https://example.org/', 'http://www.example.net/']),
		  textafter = '\n'.join(['http://www.example.net/', 'https://example.org/']),
		  textafterpatterns = None,
		  savecomment = 'BOT - Sorting list',
		 ),
		TestPage(
		  title = 'ArchiveBot/Sorting',
		  textbefore = '<!-- bot --><!-- /bot -->',
		  textafter = None,
		  textafterpatterns = ['^<!-- bot -->$', r'example\.net.*\{\{notsaved\}\}', r'example\.org.*\{\{notsaved\}\}', '^<!-- /bot -->$'],
		  savecomment = 'BOT - Updating page: {{saved}} (0), {{notsaved}} (2), Total size (0&nbsp;KiB)',
		 ),

		TestPage(title = 'ArchiveBot/Sections/list', textbefore = '\n'.join(['https://example.net/', 'https://example.org/', '', '== Foo ==', 'https://archive.org/', 'https://archiveteam.org/']), textafter = None, textafterpatterns = None, savecomment = None),
		TestPage(
		  title = 'ArchiveBot/Sections',
		  textbefore = 'Look at these sections:\n\n== Start ==\n<!-- bot --><!-- /bot -->\n\n== Just foo ==\n<!-- bot:Foo --><!-- /bot -->',
		  textafter = None,
		  textafterpatterns = [
		    '^Look at these sections:$', '^$',
		    '^== Start ==$', '^<!-- bot -->$', r'example\.net.*\{\{notsaved\}\}', r'example\.org.*\{\{notsaved\}\}', '<!-- /bot -->$',
		    '^== Just foo ==$', '^<!-- bot:Foo -->$', r'archive\.org.*\{\{notsaved\}\}', r'archiveteam\.org.*\{\{notsaved\}\}', '<!-- /bot -->$',
		   ],
		  savecomment = 'BOT - Updating page: {{saved}} (0), {{notsaved}} (4), Total size (0&nbsp;KiB)',
		 ),

		TestPage(title = 'ArchiveBot/Broken Sections/list', textbefore = '== Title ==\nhttps://example.org/', textafter = None, textafterpatterns = None, savecomment = None),
		TestPage(title = 'ArchiveBot/Broken Sections', textbefore = 'Introduction\n<!-- bot:title --><!-- /bot -->\nEpilogue', textafter = None, textafterpatterns = None, savecomment = None),

		TestPage(title = 'ArchiveBot/Saved sites/list', textbefore = '\n'.join(['http://alsosaved.example.net/', 'https://savedsite.example.com/']), textafter = None, textafterpatterns = None, savecomment = None),
		TestPage(
		  title = 'ArchiveBot/Saved sites',
		  textbefore = '<!-- bot --><!-- /bot -->',
		  textafter = None,
		  textafterpatterns = [
		    '^<!-- bot -->',
		    r'rowspan=2.*alsosaved\.example\.net.*rowspan=2.*\{\{saved\}\}',
		    r'https://archive\.fart\.website/archivebot/viewer/domain/alsosaved\.example\.net.*2019-01-01',
		    r'https://archive\.fart\.website/archivebot/viewer/domain/alsosaved\.example\.net.*2019-02-01',
		    r'savedsite\.example\.com.*\{\{saved\}\}',
		    '^<!-- /bot -->$',
		   ],
		  savecomment = 'BOT - Updating page: {{saved}} (2), {{notsaved}} (0), Total size (25&nbsp;KiB)',
		 ),

		TestPage(title = 'ArchiveBot/Transfersh/list', textbefore = '\n'.join(['https://transfer.sh/23456/bar', 'https://transfer.sh/12345/foo']), textafter = None, textafterpatterns = None, savecomment = None),
		TestPage(title = 'ArchiveBot/Transfersh', textbefore = '<!-- bot --><!-- /bot -->', textafter = None, textafterpatterns = ['^'], savecomment = 'BOT - Updating page: {{saved}} (0), {{notsaved}} (2), Total size (0&nbsp;KiB)'), # Don't care about this, just needed to trigger the /list processing

		TestPage(title = 'ArchiveBot/Ixio/list', textbefore = '\n'.join(['http://ix.io/23456+/bar', 'http://ix.io/12345+/foo']), textafter = None, textafterpatterns = None, savecomment = None),
		TestPage(title = 'ArchiveBot/Ixio', textbefore = '<!-- bot --><!-- /bot -->', textafter = None, textafterpatterns = ['^'], savecomment = 'BOT - Updating page: {{saved}} (0), {{notsaved}} (2), Total size (0&nbsp;KiB)'),
	]

	viewerData = {
		# url -> return values
		# Any URL not appearing here implicitly returns no results
		'http://alsosaved.example.net/': (True, 'https://archive.fart.website/archivebot/viewer/?q=http://alsosaved.example.net/',
		  '| [https://archive.fart.website/archivebot/viewer/domain/alsosaved.example.net alsosaved.example.net] || [https://archive.fart.website/archivebot/viewer/job/12345 12345] || 2019-01-01 || data-sort-value=12345 | {{green|12.1 KiB}}' +
		  '\n|-\n' +
		  '| [https://archive.fart.website/archivebot/viewer/domain/alsosaved.example.net alsosaved.example.net] || [https://archive.fart.website/archivebot/viewer/job/12345 12345] || 2019-02-01 || data-sort-value=12345 | {{green|12.1 KiB}}',
		  24690),
		'https://savedsite.example.com/': (True, 'https://archive.fart.website/archivebot/viewer/?q=https://savedsite.example.com/',
		  '| [https://archive.fart.website/archivebot/viewer/domain/savedsite.example.com savedsite.example.com] || [https://archive.fart.website/archivebot/viewer/job/23456 23456] || 2019-03-01 || data-sort-value=1024 | {{green|1.0 KiB}}',
		  1024),
	}

	ok = 0
	fail = 0

	with mock([p.title for p in pagesData], viewerData) as (catalogue, Page):
		for pageData in pagesData:
			catalogue.add_page(Page.make(pageData.title, pageData.textbefore))

		f = io.StringIO()
		with contextlib.redirect_stdout(f):
			archivebot.main()
		output = f.getvalue()

		#TODO: Add output checks
		#TODO: Add more broken pages

		for pageData in pagesData:
			page = catalogue.get_page(pageData.title)
			if pageData.textafterpatterns is not None:
				lines = iter(page.text.split('\n'))
				line = next(lines)
				failed = False
				for pattern in pageData.textafterpatterns:
					while re.search(pattern, line) is None:
						line = next(lines, None)
						if line is None:
							failed = True
							break
					if failed:
						break
				if failed:
					print('Page {} text FAIL: pattern fault'.format(pageData.title))
					fail += 1
				else:
					print('Page {} text OK'.format(pageData.title))
					ok += 1
			else:
				expectedText = pageData.textafter if pageData.textafter is not None else pageData.textbefore
				if page.text != expectedText:
					print('Page {} text FAIL:'.format(pageData.title))
					print('Expected:')
					print(repr(expectedText))
					print('Got:')
					print(repr(page.text))
					print('')
					fail += 1
				else:
					print('Page {} text OK'.format(pageData.title))
					ok += 1

			if not (pageData.savecomment is None and page.savecomment is None) and pageData.savecomment != page.savecomment:
				print('Page {} save comment FAIL:'.format(pageData.title))
				print('Expected: {!r}'.format(pageData.savecomment))
				print('Got: {!r}'.format(page.savecomment))
				fail += 1
			else:
				print('Page {} save comment OK'.format(pageData.title))
				ok += 1

	print('main OK: {}, fail: {}'.format(ok, fail))


def test_parselistline():
	inputLine = object() # Singleton to represent the input line (stripped)

	def make_test_entry(iLine, sorturl, url, label, line = inputLine):
		f = lambda x: x if x is not inputLine else iLine.strip()
		return (iLine, archivebot.Entry(sorturl = f(sorturl), url = f(url), label = f(label), line = f(line)))

	tests = [
		# (input line str, output Entry)
		make_test_entry(iLine = 'https://example.org/', sorturl = 'example.org/', url = inputLine, label = None),
		make_test_entry(iLine = ' https://www.example.net/', sorturl = 'example.net/', url = inputLine, label = None),
		make_test_entry(iLine = 'https://transfer.sh/fileid/filename', sorturl = 'transfer.sh/filename', url = inputLine, label = None),
		make_test_entry(iLine = 'https://example.org/|Example', sorturl = 'example.org/', url = 'https://example.org/', label = 'Example', line = 'https://example.org/ | Example'),
		make_test_entry(iLine = 'https://example.net', sorturl = 'example.net/', url = 'https://example.net/', label = None, line = 'https://example.net/'),
	]

	ok = 0
	fail = 0
	for line, expected in tests:
		if archivebot.parselistline(line) != expected:
			print('parselistline({!r}) failed'.format(line))
			print(archivebot.parselistline(line))
			print(expected)
			fail += 1
		else:
			ok += 1

	print('parselistline OK: {}, fail: {}'.format(ok, fail))


def test_curateurls():
	MockPage = make_mock_page(None)

	tests = [
		# (Page, sectionentries dict)

		# Simple example
		(
			MockPage.make('ArchiveBot/Simple example/list', '\n'.join(['https://www.example.com/', 'http://example.org', 'https://example.net/', 'http://example.net/foo'])),
			{
				None: [
					archivebot.Entry(sorturl = 'example.com/', url = 'https://www.example.com/', label = None, line = 'https://www.example.com/'),
					archivebot.Entry(sorturl = 'example.net/', url = 'https://example.net/', label = None, line = 'https://example.net/'),
					archivebot.Entry(sorturl = 'example.net/foo', url = 'http://example.net/foo', label = None, line = 'http://example.net/foo'),
					archivebot.Entry(sorturl = 'example.org/', url = 'http://example.org/', label = None, line = 'http://example.org/'),
				],
			},
		),

		# Duplicate filtering
		(
			MockPage.make('ArchiveBot/Duplicates/list', '\n'.join(['https://example.org', 'https://example.org/'])),
			{None: [archivebot.Entry(sorturl = 'example.org/', url = 'https://example.org/', label = None, line = 'https://example.org/')]},
		),

		# Near-duplicate handling
		(
			MockPage.make('ArchiveBot/Near-duplicates/list', '\n'.join(['https://example.org/', 'https://example.org/ | Example', 'http://www.example.org/'])),
			{None: [
				archivebot.Entry(sorturl = 'example.org/', url = 'http://www.example.org/', label = None, line = 'http://www.example.org/'),
				archivebot.Entry(sorturl = 'example.org/', url = 'https://example.org/', label = None, line = 'https://example.org/'),
				archivebot.Entry(sorturl = 'example.org/', url = 'https://example.org/', label = 'Example', line = 'https://example.org/ | Example'),
			]},
		),
	]

	ok = 0
	fail = 0
	for page, expected in tests:
		out = archivebot.curateurls(page)
		if out != expected:
			print('curateurls for page {} failed'.format(page.title()))
			print('Expected:')
			print(repr(expected))
			print('Got:')
			print(repr(out))
			fail += 1
		else:
			ok += 1

	print('curateurls OK: {}, fail: {}'.format(ok, fail))


def test():
	test_parselistline()
	test_curateurls()
	test_main()


if __name__ == '__main__':
	test()
