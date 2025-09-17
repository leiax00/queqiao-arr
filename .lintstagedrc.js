module.exports = {
  'backend/**/*.py': [
    'black --check',
    'ruff check',
    'mypy'
  ],
  'frontend/**/*.{js,ts,vue}': [
    'eslint --fix',
    'vue-tsc --noEmit'
  ],
  '*.md': [
    'prettier --write'
  ]
};
