'use strict';

const js = require('@eslint/js');
const globals = require('globals');
const esX = require('eslint-plugin-es-x');

module.exports = [
    {
        ignores: ['node_modules/', 'docs/_build/', '.venv/'],
    },
    js.configs.recommended,
    {
        files: ['src/docs_versions_menu/_js/**/*.js'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'script',
            globals: {
                ...globals.browser,
                module: 'writable',
            },
        },
    },
    {
        // Flag ECMAScript syntax/standard-library features newer than
        // ES2020, so the code stays compatible with older browsers. This
        // only covers language-level features (e.g. optional chaining,
        // Array.prototype.at), never Web/DOM APIs like fetch or URL, which
        // are unaffected.
        files: ['src/docs_versions_menu/_js/**/*.js'],
        ...esX.configs['flat/restrict-to-es2020'],
    },
    {
        files: ['jstests/**/*.js', 'eslint.config.js'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'commonjs',
            globals: {
                ...globals.node,
                // Tests assign a jsdom Document to global.document to
                // simulate a browser environment.
                document: 'readonly',
            },
        },
    },
];
