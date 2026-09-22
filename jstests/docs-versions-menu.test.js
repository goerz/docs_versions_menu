'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const { html: beautifyHtml } = require('js-beautify');

const docsVersionMenu = require(
    '../src/docs_versions_menu/_js/docs-versions-menu-lib.js'
);

function setWindowLocation(url) {
    global.window = new JSDOM('', { url }).window;
}

function setupDom(url) {
    const dom = new JSDOM('', { url });
    global.window = dom.window;
    global.document = dom.window.document;
}

/**
 * Mocks the global fetch function for a fixed set of URLs.
 *
 * `responses` maps a URL to what fetch should resolve for it: `true` if
 * the URL merely needs to exist (e.g. for a HEAD check), or a JSON-
 * serializable value if the response's `.json()` needs to return
 * something specific. Any URL not present in `responses` resolves as a
 * 404.
 */
function mockFetch(t, responses) {
    t.mock.method(global, 'fetch', async (url) => {
        if (!(url in responses)) {
            return { ok: false, status: 404, statusText: 'Not Found' };
        }
        return {
            ok: true,
            status: 200,
            statusText: 'OK',
            json: async () => responses[url],
        };
    });
}

test('getRootUrl', async (t) => {
    t.afterEach(() => {
        delete global.window;
    });

    await t.test(
        'walks up the URL path until fetch finds versions.json',
        async (t) => {
            mockFetch(t, {
                'https://example.com/docs/v1.0/versions.json': true,
            });
            setWindowLocation(
                'https://example.com/docs/v1.0/guide/intro.html'
            );

            const rootUrl = await docsVersionMenu.getRootUrl();

            assert.equal(rootUrl, 'https://example.com/docs/v1.0');
        }
    );

    await t.test(
        'returns the origin when versions.json is at the root',
        async (t) => {
            mockFetch(t, { 'https://example.com/versions.json': true });
            setWindowLocation('https://example.com/');

            const rootUrl = await docsVersionMenu.getRootUrl();

            assert.equal(rootUrl, 'https://example.com');
        }
    );

    await t.test(
        'throws when no versions.json can be found anywhere on the path',
        async (t) => {
            mockFetch(t, {});
            setWindowLocation(
                'https://example.com/docs/v1.0/guide/intro.html'
            );

            await assert.rejects(
                () => docsVersionMenu.getRootUrl(),
                /could not find versions\.json/
            );
        }
    );
});

test('loadVersionData', async (t) => {
    t.afterEach(() => {
        delete global.window;
    });

    await t.test(
        'finds the root URL and returns the parsed versions.json',
        async (t) => {
            const versionData = {
                versions: ['v1.0'],
                labels: { 'v1.0': 'v1.0' },
                downloads: { 'v1.0': [] },
                warnings: { 'v1.0': [] },
                latest: 'v1.0',
            };
            mockFetch(t, {
                'https://example.com/docs/versions.json': versionData,
            });
            setWindowLocation(
                'https://example.com/docs/v1.0/guide/intro.html'
            );

            const data = await docsVersionMenu.loadVersionData();

            assert.deepEqual(data, versionData);
        }
    );

    await t.test(
        'throws when versions.json cannot be fetched',
        async (t) => {
            setWindowLocation('https://example.com/docs/index.html');
            t.mock.method(global, 'fetch', async (url, options) => {
                if (options && options.method === 'HEAD') {
                    // Let getRootUrl succeed, so the failure below comes
                    // from actually fetching the file's content.
                    return { ok: true, status: 200, statusText: 'OK' };
                }
                return {
                    ok: false,
                    status: 500,
                    statusText: 'Internal Server Error',
                };
            });

            await assert.rejects(
                () => docsVersionMenu.loadVersionData(),
                /500 Internal Server Error/
            );
        }
    );

    await t.test(
        'uses the given rootUrl without calling getRootUrl',
        async (t) => {
            const versionData = {
                versions: ['v1.0'],
                labels: { 'v1.0': 'v1.0' },
                downloads: { 'v1.0': [] },
                warnings: { 'v1.0': [] },
                latest: 'v1.0',
            };
            mockFetch(t, {
                'https://example.com/docs/versions.json': versionData,
            });
            setWindowLocation(
                'https://example.com/docs/v1.0/guide/intro.html'
            );

            const data = await docsVersionMenu.loadVersionData(
                'https://example.com/docs'
            );

            assert.deepEqual(data, versionData);
            // Only the versions.json GET, no HEAD request from
            // getRootUrl.
            assert.equal(global.fetch.mock.callCount(), 1);
        }
    );
});

test('getCurrentVersionFolder', (t) => {
    t.afterEach(() => {
        delete global.window;
    });

    t.test('extracts the folder right after the root URL', () => {
        setWindowLocation(
            'https://example.com/docs/v1.0/guide/intro.html'
        );

        const folder = docsVersionMenu.getCurrentVersionFolder(
            'https://example.com/docs'
        );

        assert.equal(folder, 'v1.0');
    });

    t.test(
        'also works when the root URL is the origin itself',
        () => {
            setWindowLocation('https://example.com/v1.0/index.html');

            const folder = docsVersionMenu.getCurrentVersionFolder(
                'https://example.com'
            );

            assert.equal(folder, 'v1.0');
        }
    );
});

test('_getGithubProjectUrl', (t) => {
    t.test(
        'derives the GitHub project URL from a github.io root URL',
        () => {
            const url = docsVersionMenu._getGithubProjectUrl(
                'https://goerz.github.io/docs_versions_menu'
            );

            assert.equal(
                url,
                'https://github.com/goerz/docs_versions_menu'
            );
        }
    );

    t.test(
        'still derives the project URL when the root URL has extra ' +
            'path segments after the project name',
        () => {
            const url = docsVersionMenu._getGithubProjectUrl(
                'https://goerz.github.io/docs_versions_menu/v1.0'
            );

            assert.equal(
                url,
                'https://github.com/goerz/docs_versions_menu'
            );
        }
    );

    t.test('returns null for a non-github.io root URL', () => {
        const url = docsVersionMenu._getGithubProjectUrl(
            'https://example.com/docs'
        );

        assert.equal(url, null);
    });
});

test('_buildProjectLinksSections', (t) => {
    const projectLinks = {
        'On GitLab': {
            'Project Home': 'https://gitlab.example.com/acme/widget',
            Issues: 'https://gitlab.example.com/acme/widget/-/issues',
        },
    };

    t.test(
        'renders projectLinks sections, and auto-detects a GitHub ' +
            'section when githubProjectUrl and projectLinks are both unset',
        () => {
            const sections = docsVersionMenu._buildProjectLinksSections(
                { githubProjectUrl: null, projectLinks: null },
                'https://acme.github.io/widget'
            );

            assert.deepEqual(sections, [
                [
                    'On GitHub',
                    [
                        [
                            'Project Home',
                            'https://github.com/acme/widget',
                        ],
                        [
                            'Issues',
                            'https://github.com/acme/widget/issues',
                        ],
                    ],
                ],
            ]);
        }
    );

    t.test(
        'suppresses GitHub auto-detection when projectLinks is set',
        () => {
            const sections = docsVersionMenu._buildProjectLinksSections(
                { githubProjectUrl: null, projectLinks },
                'https://acme.github.io/widget'
            );

            assert.deepEqual(sections, [
                [
                    'On GitLab',
                    [
                        [
                            'Project Home',
                            'https://gitlab.example.com/acme/widget',
                        ],
                        [
                            'Issues',
                            'https://gitlab.example.com/acme/widget/-/issues',
                        ],
                    ],
                ],
            ]);
        }
    );

    t.test(
        'appends an explicit githubProjectUrl section after the ' +
            'projectLinks sections',
        () => {
            const sections = docsVersionMenu._buildProjectLinksSections(
                {
                    githubProjectUrl: 'https://github.com/acme/widget',
                    projectLinks,
                },
                'https://example.com/docs'
            );

            assert.deepEqual(sections, [
                [
                    'On GitLab',
                    [
                        [
                            'Project Home',
                            'https://gitlab.example.com/acme/widget',
                        ],
                        [
                            'Issues',
                            'https://gitlab.example.com/acme/widget/-/issues',
                        ],
                    ],
                ],
                [
                    'On GitHub',
                    [
                        [
                            'Project Home',
                            'https://github.com/acme/widget',
                        ],
                        [
                            'Issues',
                            'https://github.com/acme/widget/issues',
                        ],
                    ],
                ],
            ]);
        }
    );
});

test('addVersionsMenu', async (t) => {
    t.afterEach(() => {
        delete global.window;
        delete global.document;
    });

    // A plain project with two versions, no downloads, no warnings.
    const basicVersionData = {
        versions: ['v1.0', 'v2.0'],
        labels: { 'v1.0': 'v1.0', 'v2.0': 'v2.0' },
        downloads: { 'v1.0': [], 'v2.0': [] },
        warnings: { 'v1.0': [], 'v2.0': [] },
        latest: 'v2.0',
    };

    // A project with a PDF download for each version, and the current
    // version (v2.0) flagged as unreleased.
    const richVersionData = {
        versions: ['v1.0', 'v2.0'],
        labels: { 'v1.0': 'v1.0', 'v2.0': 'v2.0 (dev)' },
        downloads: {
            'v1.0': [['PDF', 'v1.0/docs.pdf']],
            'v2.0': [['PDF', 'v2.0/docs.pdf']],
        },
        warnings: { 'v1.0': [], 'v2.0': ['unreleased'] },
        latest: 'v1.0',
    };

    const scenarios = [
        {
            name: 'default options (collapsed badge, no GitHub link)',
            file: 'default-options.html',
            rootUrl: 'https://example.com/docs',
            pageUrl: 'https://example.com/docs/v2.0/index.html',
            versionData: basicVersionData,
            options: {},
        },
        {
            name: 'expanded menu with a custom title',
            file: 'expanded-menu-custom-title.html',
            rootUrl: 'https://example.com/docs',
            pageUrl: 'https://example.com/docs/v2.0/index.html',
            versionData: basicVersionData,
            options: { badgeOnly: false, menuTitle: 'My Project Docs' },
        },
        {
            name: 'explicit GitHub project URL',
            file: 'explicit-github-url.html',
            rootUrl: 'https://example.com/docs',
            pageUrl: 'https://example.com/docs/v2.0/index.html',
            versionData: basicVersionData,
            options: {
                githubProjectUrl: 'https://github.com/acme/widget',
            },
        },
        {
            name: 'GitHub project URL auto-detected from a github.io root',
            file: 'auto-detected-github-url.html',
            rootUrl: 'https://acme.github.io/widget',
            pageUrl: 'https://acme.github.io/widget/v2.0/index.html',
            versionData: basicVersionData,
            options: {},
        },
        {
            name: 'GitHub section explicitly disabled on a github.io root',
            file: 'github-url-disabled.html',
            rootUrl: 'https://acme.github.io/widget',
            pageUrl: 'https://acme.github.io/widget/v2.0/index.html',
            versionData: basicVersionData,
            options: { githubProjectUrl: '' },
        },
        {
            name: 'downloads and an unreleased-version warning banner',
            file: 'downloads-and-warning.html',
            rootUrl: 'https://example.com/docs',
            pageUrl: 'https://example.com/docs/v2.0/index.html',
            versionData: richVersionData,
            options: { badgeOnly: false },
        },
        {
            name:
                'custom project links, with GitHub auto-detection ' +
                'suppressed on a github.io root',
            file: 'project-links.html',
            rootUrl: 'https://acme.github.io/widget',
            pageUrl: 'https://acme.github.io/widget/v2.0/index.html',
            versionData: basicVersionData,
            options: {
                projectLinks: {
                    'On GitLab': {
                        'Project Home':
                            'https://gitlab.example.com/acme/widget',
                        Issues:
                            'https://gitlab.example.com/acme/widget/-/issues',
                    },
                },
            },
        },
        {
            name:
                'custom project links combined with an explicit ' +
                'GitHub project URL',
            file: 'project-links-and-github-url.html',
            rootUrl: 'https://example.com/docs',
            pageUrl: 'https://example.com/docs/v2.0/index.html',
            versionData: basicVersionData,
            options: {
                githubProjectUrl: 'https://github.com/acme/widget',
                projectLinks: {
                    'On GitLab': {
                        'Project Home':
                            'https://gitlab.example.com/acme/widget',
                    },
                },
            },
        },
    ];

    for (const scenario of scenarios) {
        await t.test(scenario.name, async (t) => {
            mockFetch(t, {
                [`${scenario.rootUrl}/versions.json`]: scenario.versionData,
            });
            setupDom(scenario.pageUrl);

            const returned = await docsVersionMenu.addVersionsMenu(
                scenario.options
            );

            assert.deepEqual(returned, scenario.versionData);
            t.assert.fileSnapshot(
                beautifyHtml(document.body.innerHTML, { indent_size: 2 }),
                path.join(__dirname, 'snapshots', scenario.file),
                { serializers: [(html) => html] }
            );
        });
    }

    await t.test(
        'rejects when versions.json cannot be fetched',
        async (t) => {
            setupDom('https://example.com/docs/index.html');
            t.mock.method(global, 'fetch', async (url, options) => {
                if (options && options.method === 'HEAD') {
                    // Let getRootUrl succeed, so the failure below comes
                    // from actually fetching the file's content.
                    return { ok: true, status: 200, statusText: 'OK' };
                }
                return {
                    ok: false,
                    status: 500,
                    statusText: 'Internal Server Error',
                };
            });

            await assert.rejects(
                () => docsVersionMenu.addVersionsMenu(),
                /500 Internal Server Error/
            );
        }
    );
});
