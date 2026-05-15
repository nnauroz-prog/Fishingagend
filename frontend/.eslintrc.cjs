module.exports = {
  root: true,
  env: { browser: true, es2022: true, node: true },
  extends: ['eslint:recommended', 'plugin:vue/vue3-recommended'],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    parser: '@typescript-eslint/parser',
  },
  rules: {
    'vue/multi-word-component-names': 'off',
  },
};
