name: 🐞 Bug report
description: Create a report to help us improve
title: "[Bug] <title>"
labels: [bug]
assignees: []

body:
  - type: markdown
    attributes:
      value: "## Please fill out this form to report the bug."

  - type: input
    id: what-happened
    attributes:
      label: What happened?
      description: Describe the bug clearly and concisely.
      placeholder: Bug description
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      placeholder: |
        1. Go to '...'
        2. Click on '...'
        3. See error
    validations:
      required: true

  - type: dropdown
    id: severity
    attributes:
      label: Severity
      options:
        - Low
        - Medium
        - High
        - Critical

  - type: textarea
    id: context
    attributes:
      label: Additional context
      placeholder: Logs, screenshots, or related issues
